import logging
import traceback

from PyQt5 import uic
from PyQt5.QtWidgets import *

from utils import (
    path_helper as ph,
    log_filter as lf
)
from windows import alert_box as box
from handlers import event_filter as ef
from lumiel_bot import main as lumiel


PROJECT_ROOT = ph.find_dir("gui_discord_bot")
UI_DIR = PROJECT_ROOT / "uis"

main_window = uic.loadUiType(UI_DIR / "mainWindow.ui")[0]
info_dialog = uic.loadUiType(UI_DIR / "dialog" / "infoDialog.ui",
                             from_imports=True, import_from='resources')[0]

# TODO: 메인 윈도우 구현
'''
TODOs:
    (ui기준 위에서부터 정렬)
    - 메뉴 바
        - 정보
            - 정보 **완료**
            - github => 브라우저로 바로 연결
        - 설정 => 바로 설정창으로 이동
    ---------------------------------------------------------------
    - 타이틀 레이블 **완료**
    - 로그아웃 버튼 **완료**
    - 채널에 메시지 전송 **완료**
    - 명령어 편집기 버튼 => 일단 셀렉터 이동하는데 까지만 만들기
    - 유틸리티 버튼 => 유틸리티를 이벤트로 변경해서 설정에서도 나왔던 하드코딩된 부분이나, 커맨드처럼 사용자화할 수 있도록 하는 기능 구현
    - 로그 레벨 콤보박스 **완료**
    - 로그 레벨 적용 버튼 **완료**
    - 로그 출력창 **완료**
      ㄴ 로그 파일 인식해서 불러오는 방식이나, 핸들러같은거 연결해야함.
         일단 할려면 모듈 하나 필요.
'''


class MainWindow(QMainWindow, main_window):

    def __init__(self, event_filter: ef.EventFilter, bot: lumiel.LumielBot):
        super().__init__()
        self.logger = logging.getLogger("Logger")

        self.bot = bot
        self.bot.signal.connect(self.signal_handler)

        self.event_filter = event_filter

        self.setupUi(self)
        self.show()

        self.level = logging.INFO

        self.titleLabel.setText(f"{self.bot.bot.user.name}님 환영합니다!")

        self.logoutPushButton.clicked.connect(self.logout)
        self.logLevelSavePushButton.clicked.connect(self.level_save)
        self.messageSendPushButton.clicked.connect(self.send_message)
        self.messageLineEdit.returnPressed.connect(self.send_message)

        self.openInfo.triggered.connect(self.open_info)

        self.init_logTextBrowser()
        self.init_channelSelectComboBox()

    def open_info(self):
        self.event_filter.self_close = True
        InfoDialog().exec_()

    def logout(self):
        reply = box.create_box("로그아웃 하시겠습니까?", QMessageBox.Question, "로그아웃").exec_()
        if reply == QMessageBox.StandardButton.Yes:
            self.event_filter.ignore_reply = True
            self.close()

    def signal_handler(self, payload):
        if payload[0] == lumiel.ON_LOGGING:
            self.logger.debug(f"MainWindow.signal: 로그 시그널 수신됨. message: {payload[1]}")
            if lf.log_inspector(payload[2][0], self.level):
                self.logger.debug("설정된 로그 레벨에 도달함.")
                self.logTextBrowser.append(payload[2][0])
                scroll_bar = self.logTextBrowser.verticalScrollBar()
                scroll_bar.setValue(scroll_bar.maximum())
            else:
                self.logger.debug("설정된 로그 레벨에 도달하지 않음.")
        elif payload[0] == lumiel.SEND_MESSAGE_ERROR:
            exc_type = type(payload[2][0])
            exc_value = str(payload[2][0])
            exc_tb = "".join(
                traceback.format_exception(
                    type(payload[2][0]), payload[2][0], payload[2][0].__traceback__
                )
            )

            log_msg = (
                f"\n[Unhandled Exception]\n"
                f"Type: {exc_type}\n"
                f"Message: {exc_value}\n"
                f"Traceback:\n{exc_tb}"
            )
            logging.error(log_msg)
            box.create_box("메시지 전송 도중 오류 발생", QMessageBox.Warning).exec_()
        elif payload[0] == lumiel.CHANNEL_NOT_FOUND:
            box.create_box("채널을 찾을 수 없습니다.", QMessageBox.Warning).exec_()
        elif payload[0] == lumiel.SEND_SUCCESS:
            box.create_box("메시지가 성공적으로 전송되었습니다.", QMessageBox.Information).exec_()

    def level_save(self):
        level_indexes = {
            0: logging.DEBUG,
            1: logging.INFO,
            2: logging.WARNING,
            3: logging.ERROR,
        }
        self.level = level_indexes[self.logLevelSelectComboBox.currentIndex()]
        self.logger.debug(f"로그 레벨 저장 및 로드됨. level: {self.level}")
        log = lf.log_filter(self.level, "lumiel_bot.main")
        self.logTextBrowser.setPlainText(log)
        scroll_bar = self.logTextBrowser.verticalScrollBar()
        scroll_bar.setValue(scroll_bar.maximum())

    def init_logTextBrowser(self):
        log = lf.log_filter(self.level, "lumiel_bot.main")
        self.logTextBrowser.setPlainText(log)
        scroll_bar = self.logTextBrowser.verticalScrollBar()
        scroll_bar.setValue(scroll_bar.maximum())
        self.logger.debug("logTextBrowser 초기화됨.")

    def init_channelSelectComboBox(self):
        self.channelSelectComboBox.addItems(list(self.bot.channels))
        self.channelSelectComboBox.view().setMinimumWidth(300)
        self.logger.debug("channelSelectComboBox 초기화됨.")

    def send_message(self):
        self.logger.debug(
            f"메시지 전송이 요청되었습니다.\n"
            f"message: {self.messageLineEdit.text()}\n"
            f"channel: {self.bot.channels[self.channelSelectComboBox.currentText()]}"
        )
        if self.messageLineEdit.text() == "":
            box.create_box("메시지를 입력하세요.", QMessageBox.Warning).exec_()
            return
        self.bot.signal.emit(
            (
                lumiel.DO_SEND_MESSAGE,
                "메시지가 전송이 요청되었습니다.",
                (
                    self.messageLineEdit.text(),
                    self.bot.channels[self.channelSelectComboBox.currentText()]
                )
            )
        )
        self.messageLineEdit.clear()


class InfoDialog(QDialog, info_dialog):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.show()
