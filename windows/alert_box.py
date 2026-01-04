import sys
import logging
from PyQt5.QtWidgets import QApplication, QMessageBox

_logger = logging.getLogger("Logger")


def create_box(msg: str, level: int, title: str = None) -> QMessageBox:
    '''
    QMessageBox를 생성하는 메서드

    :param msg: 표시할 입력 문구
    :param level: 창의 종류(경고 단계, QMessageBox상수 사용)
    :param title: 창의 제목, None일 시 단계에 따라 설정
    :return: QMessageBox인스턴스
    '''

    default_titles = {
        QMessageBox.Information: "안내",
        QMessageBox.Warning: "경고",
        QMessageBox.Question: "확인",
        QMessageBox.Critical: "오류"
    }

    logging_tags = {
        QMessageBox.Information: "[information box]",
        QMessageBox.Warning: "[warning box]",
        QMessageBox.Question: "[question box]",
        QMessageBox.Critical: "[critical box]"
    }
    
    if level not in default_titles:
        raise ValueError("유효하지 않은 메시지 레벨")

    if title is None:
        title = default_titles[level]

    logging_tag = logging_tags[level]

    _logger.debug(
        f"\n{logging_tag}\n"
        f"Title: {title}\n"
        f"Message: {msg}"
    )

    msg_box = QMessageBox()
    msg_box.setIcon(level)
    msg_box.setText(msg)
    msg_box.setWindowTitle(title)
    if level == QMessageBox.Question:
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

    return msg_box


app = QApplication.instance() or QApplication(sys.argv)

