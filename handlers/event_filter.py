from PyQt5.QtCore import QObject, QEvent
from PyQt5.QtWidgets import QMessageBox, QMenu
from PyQt5.QtGui import QWindow
from PyQt5.QtCore import QThread
import logging
import os
from windows import alert_box

_logger = logging.getLogger("Logger")


class EventFilter(QObject):
    def __init__(self):
        super().__init__()
        self.ignore_reply = False
        self.self_close = False
        self.ignore_event = False
        self.bot_thread = None

    def set_bot_thread(self, thread: QThread) -> None:
        self.bot_thread = thread
    
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Close:
            _logger.debug(f"종료 요청됨:\n"
                          f"obj: {obj}\n"
                          f"event: {event}")
            
            if self.ignore_reply:
                self.ignore_reply = False
                _logger.debug("확인창 무시 후 애플리케이션 종료 요청")
                if self.bot_thread is not None:
                    self.bot_thread.quit()
                    self.bot_thread.wait()
                event.accept()
                _logger.info("애플리케이션 종료 완료")
                os._exit(0)

            if self.self_close:
                self.self_close = False
                _logger.debug("확인창 무시 후 본인만 종료")
                event.accept()
                return False

            if self.ignore_event:
                self.ignore_event = False
                _logger.debug("종료 이벤트 무시")
                event.ignore()
                return True

            if isinstance(obj, QMenu) or isinstance(obj, QWindow):
                event.accept()
                return False

            from windows import main_window
            if isinstance(obj, QMessageBox):
                _logger.debug("QMessageBox의 종료창 무시 후 본인 종료")
                event.accept()
                return False
            elif isinstance(obj, main_window.InfoDialog):
                _logger.debug("InfoDialog의 종료창 무시 후 본인 종료")
                event.accept()
                return False

            _logger.debug(self.bot_thread)
            box = alert_box.create_box("정말 종료하시겠습니까?", QMessageBox.Question, "종료")
            reply = box.exec_()
            if reply == QMessageBox.StandardButton.Yes:
                _logger.debug("애플리케이션 종료 승인됨")
                if self.bot_thread is not None:
                    self.bot_thread.quit()
                    self.bot_thread.wait()
                event.accept()
                _logger.info("애플리케이션 종료 완료")
                os._exit(0)
            else:
                _logger.info("애플리케이션 종료 취소됨")
                event.ignore()
                return True
        return False
