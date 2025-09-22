import sys
from PyQt5.QtWidgets import QApplication, QMessageBox
import traceback as tb
import logging
from PyQt5.QtCore import QThread
import os

_logger = logging.getLogger("Logger")

bot_thread: QThread = None


def set_thread(t):
    global bot_thread
    bot_thread = t


def global_exception_hook(exctype, value, traceback):
    tb_str = "".join(tb.format_tb(traceback))

    log_msg = (
        f"\n[Unhandled Exception]\n"
        f"Type: {exctype.__name__}\n"
        f"Message: {value}\n"
        f"Traceback:\n{tb_str}"
    )

    _logger.error(log_msg)

    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setText(str(value))
    msg.setWindowTitle("오류")
    msg.exec_()
    logging.shutdown()

    if bot_thread is not None:
        bot_thread.quit()
        bot_thread.wait(5000)
    os._exit(1)


sys.excepthook = global_exception_hook

app = QApplication(sys.argv)
