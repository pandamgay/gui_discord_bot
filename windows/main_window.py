import logging

from PyQt5 import uic
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import *

from utils import path_helper as ph


PROJECT_ROOT = ph.find_dir("gui_discord_bot")
UI_DIR = PROJECT_ROOT / "uis"

main_window = uic.loadUiType(UI_DIR / "mainWindow.ui")[0]

# TODO: 메인 윈도우 구현
'''
TODOs:
    (ui기준 위에서부터 정렬)
    - 메뉴 바
        - 정보
            - 정보
            - github => 브라우저로 바로 연결
        - 설정 => 바로 설정창으로 이동
    ---------------------------------------------------------------
    - 타이틀 레이블 **완료**
    - 로그아웃 버튼
    - 채널에 메시지 전송
    - 명령어 편집기 버튼 => 일단 셀렉터 이동하는데 까지만 만들기
    - 유틸리티 버튼 => 상태 보고 넣을지 딴걸로 바꿀지 고민중
    - 로그 레벨 콤보박스
    - 로그 레벨 적용 레이블
    - 로그 출력창
      ㄴ 로그 파일 인식해서 불러오는 방식이나, 핸들러같은거 연결해야함.
         일단 할려면 모듈 하나 필요.
'''


class MainWindow(QMainWindow, main_window):

    def __init__(self, event_filter: QObject, bot: QObject):
        super().__init__()
        self.logger = logging.getLogger("Logger")

        self.bot = bot

        self.event_filter = event_filter

        self.setupUi(self)
        self.show()

        self.titleLabel.setText(f"{self.bot.bot.user.name}님 환영합니다!")
        # self.logoutPushButton.clicked.connect(self.logout)

    # def logout(self):
