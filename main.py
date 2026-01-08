import os
import shutil
import sys
import logging
from typing import Tuple

from PyQt5 import uic
from PyQt5.QtCore import QThread
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *

from lumiel_bot import main as lumiel
from utils import (
    my_logger as ml,
    token_crypto as tc,
    token_vault as tv,
    token_validation as tval,
    path_helper as ph
)
from handlers import (
    error_handler,
    event_filter as ef
)
from windows import (
    alert_box as box,
    main_window
)


PROJECT_ROOT = ph.find_dir("gui_discord_bot")
CONFIG_DIR = PROJECT_ROOT / "config"
UI_DIR = PROJECT_ROOT / "uis" / "dialog"

start_window = uic.loadUiType(UI_DIR / "inputTokenDialog.ui")[0]
loading_window = uic.loadUiType(UI_DIR / "InitializingBotDialog.ui")[0]

_logger = ml.MyLogger(True, "./logs")
_logger = _logger.initLogger("Logger")

event_filter = ef.EventFilter()
'''
전역 종료 핸들러는 무시해야할 경우가 있기에, 항상 생성자로 받아야 함.
'''


class StartWindow(QDialog, start_window):

    def __init__(self):
        super().__init__()

        self.bot = lumiel.LumielBot()
        self.bot.signal.connect(self.login_handle)
        _logger.debug(f"StartWindow.signal: {self.bot.signal}")

        for name, logger in logging.root.manager.loggerDict.items():
            if name.startswith("discord"):
                l = logging.getLogger(name)
                l.handlers.clear()
                l.propagate = False

        result = self.token_check()

        if not result[0]:
            self.setupUi(self)
            self.show()

            self.buttonBox.accepted.disconnect()
            self.buttonBox.accepted.connect(self.bot_login)

            self.newTokenButton.setParent(None)
            self.newTokenButton.deleteLater()
        if result[1]:
            event_filter.ignore_reply = True
            self.close()

    def bot_login(self):
        TOKEN = self.inputTokenLine.text()
        if TOKEN:
            _logger.debug("입력한 토큰 로드됨")

        token_validation = tval.token_validation(TOKEN)
        _logger.debug(token_validation)

        if not token_validation[0] and not token_validation[1]:
            _logger.warning("올바른 토큰이 아님")
            box.create_box("토큰이 올바르지 않습니다.", QMessageBox.Warning).exec_()
            return
        elif not TOKEN:
            _logger.warning("입력된 토큰이 없음")
            box.create_box("토큰을 입력하세요.", QMessageBox.Warning).exec_()
            return
        elif token_validation[1]:
            _logger.error(f"알 수 없는 예외 발생:\n"
                          f"{token_validation[1]}")
            raise Exception("알 수 없는 오류가 발생했습니다.")

        save_token = self.saveTokenBox.isChecked()
        if save_token:
            SetPasswordWindow(TOKEN).exec_()

        self.accept()
        bot_thread = BotThread(TOKEN, self.bot)
        bot_thread.start()
        event_filter.set_bot_thread(bot_thread)
        error_handler.set_thread(bot_thread)

        loading = LoadingWindow(self.bot)
        loading.exec_()

    def login_handle(self, payload):
        if lumiel.BOT_INIT_SUCCESS == payload[0]:
            _logger.debug(f"StartWindow: 시그널 수신됨. message: {payload[1]}")
            self.main = main_window.MainWindow(event_filter, self.bot)
            self.main.show()

    def token_check(self) -> Tuple[bool, bool]:
        '''
        저장된 토큰이 존재하는지 확인하는 함수

        :return:
            토큰 입력창 무시 여부
            프로세스 종료 여부
        '''

        token_file = os.path.join(PROJECT_ROOT, "config", "token.bin")
        salt_file = os.path.join(PROJECT_ROOT, "config", "salt.bin")

        if os.path.exists(token_file) and os.path.exists(salt_file):
            password_window = InputPasswordWindow()
            password_window.exec_()
            _logger.debug("저장된 토큰이 존재함")
            result = password_window.user_result()

            if not result[0] and result[1]:
                _logger.debug("입력한 비밀번호가 일치함")
                token = result[1]

                bot_thread = BotThread(token, self.bot)
                bot_thread.start()
                event_filter.set_bot_thread(bot_thread)
                error_handler.set_thread(bot_thread)

                loading = LoadingWindow(self.bot)
                loading.exec_()
                return (True, False)

            elif result[0]:
                _logger.debug(
                    f"새 토큰을 만듦\n"
                    f"is_removed: {result[0]}, token: {result[1]}, is_close: {result[2]}"
                    )
                return (False, False)

            elif result[2]:
                _logger.debug(
                    f"창을 닫음\n"
                    f"is_removed: {result[0]}, token: {result[1]}, is_close: {result[2]}"
                    )
                return (True, True)
            else:
                _logger.debug(
                    f"else\n"
                    f"is_removed: {result[0]}, token: {result[1]}, is_close: {result[2]}"
                )
                return (False, False)
        else:
            _logger.debug("저장된 토큰이 발견되지 않음")
            return (False, False)


class BotThread(QThread):
    def __init__(self, token: str, bot: lumiel.LumielBot):
        super().__init__()
        self.token = token
        self.bot = bot
        self.bot.signal.connect(self.signal_handle)

    def run(self):
        self.bot.run_lumiel(self.token)

    def quit(self):
        self.bot.stop()
        _logger.debug("봇 중지 신호 전송됨")
        super().quit()

    def signal_handle(self, payload):
        if lumiel.ON_ERROR == payload[0]:
            _logger.debug(f"BotThread: 시그널 수신됨. message: {payload[1]}")
            exc_type, exc_value, exc_tb = payload[2]

            log_msg = (
                f"\n[Unhandled Exception]\n"
                f"Type: {exc_type}\n"
                f"Message: {exc_value}\n"
                f"Traceback:\n{exc_tb}"
            )
            _logger.error(log_msg)
            box.create_box(
                "봇 실행 중 오류가 발생했습니다.",
                QMessageBox.Critical
            ).exec_()
        if lumiel.ON_CRITICAL == payload[0]:
            _logger.debug(f"BotThread: 시그널 수신됨. message: {payload[1]}")
            exc_type, exc_value, exc_tb = payload[2]

            log_msg = (
                f"\n[Unhandled Exception]\n"
                f"Type: {exc_type}\n"
                f"Message: {exc_value}\n"
                f"Traceback:\n{exc_tb}"
            )
            _logger.error(log_msg)
            raise Exception("봇 실행 중 치명적 오류가 발생해 프로그램을 중단합니다.")


class LoadingWindow(QDialog, loading_window):
    def __init__(self, bot: lumiel.LumielBot):
        super().__init__()
        self.bot = bot
        self.bot.signal.connect(self.login_handle)
        _logger.debug(f"LoadingWindow.signal: {self.bot.signal}")

        self.setupUi(self)
        self.show()

    def login_handle(self, payload):
        if lumiel.BOT_INIT_SUCCESS == payload[0]:
            _logger.debug(f"LoadingWindow: 시그널 수신됨. message: {payload[1]}")
            self.accept()


class SetPasswordWindow(QDialog, start_window):

    def __init__(self, token):
        super().__init__()

        self.token = token

        self.setupUi(self)
        self.show()

        self.label.setText("설정할 비밀번호를 입력하세요:")
        self.saveTokenBox.setText("입력 보기")
        self.inputTokenLine.setEchoMode(QLineEdit.Password)

        self.newTokenButton.setParent(None)
        self.newTokenButton.deleteLater()

        self.saveTokenBox.stateChanged.connect(self.handle_check)
        self.buttonBox.accepted.connect(self.save_token)

    def handle_check(self, state):
        if state:
            self.inputTokenLine.setEchoMode(QLineEdit.Normal)
        else:
            self.inputTokenLine.setEchoMode(QLineEdit.Password)

    def save_token(self):
        token, salt = tc.encrypt_token(self.token, self.inputTokenLine.text())
        tv.save_token(token, salt)


class InputPasswordWindow(QDialog, start_window):

    def __init__(self):
        super().__init__()

        self.setupUi(self)
        self.show()

        self.label.setText("비밀번호를 입력하세요:")
        self.saveTokenBox.setText("입력 보기")
        self.inputTokenLine.setEchoMode(QLineEdit.Password)

        self.newTokenButton.clicked.connect(self.new_token)
        self.buttonBox.accepted.disconnect()
        self.buttonBox.accepted.connect(self.token_check)
        self.saveTokenBox.stateChanged.connect(self.handle_check)

        self.token = None
        self.is_removed = False
        self.is_close = True

    def new_token(self):
        shutil.rmtree(os.path.join(PROJECT_ROOT, "config"))
        self.is_removed = True
        event_filter.self_close = True
        self.close()

    def token_check(self):
        token, salt = tv.load_token()
        try:
            self.token = tc.decrypt_token(token, self.inputTokenLine.text(), salt).decode("utf-8")
        except ValueError:
            box.create_box("비밀번호가 일치하지 않습니다.", QMessageBox.Warning).exec_()
            return
        event_filter.self_close = True
        self.close()

    def handle_check(self, state):
        if state:
            self.inputTokenLine.setEchoMode(QLineEdit.Normal)
        else:
            self.inputTokenLine.setEchoMode(QLineEdit.Password)

    def closeEvent(self, event):
        event.accept()

    def user_result(self) -> Tuple[bool, str, bool]:
        return (self.is_removed, self.token, self.is_close)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.installEventFilter(event_filter)
    app.setWindowIcon(QIcon(str(PROJECT_ROOT / "resources" / "icons.ico")))

    window = StartWindow()
    app.exec_()
