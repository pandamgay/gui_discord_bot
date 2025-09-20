import logging
import sys
from datetime import datetime
import os
import inspect

# TODO: 로그 핸들러 추가


class MyLogger():

    def __init__(self, is_stream: bool, path: str):
        self.class_name = self.__class__.__name__
        self.log_path = path
        os.makedirs("logs", exist_ok=True)
        self.is_stream = is_stream
        self.created_module = inspect.stack()[1].frame.f_globals["__name__"]

    def initLogger(self, logger: str):
        __logger = logging.getLogger(logger)

        # 포매터 정의
        file_formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] ::: %(module)s.%(funcName)s:%(lineno)d >>> %(message)s"
        )

        # 핸들러 정의
        file_handler = logging.FileHandler(
            f'logs/log_{datetime.now().strftime("%Y%m%d%H%M%S")}-{self.created_module}.log',
            mode='w'
        )

        # 핸들러에 포매터 지정
        file_handler.setFormatter(file_formatter)

        # 로그 레벨 정의
        __logger.setLevel(logging.DEBUG)

        # 로거 인스턴스에 핸들러 삽입
        __logger.addHandler(file_handler)

        if self.is_stream:
            stream_formatter = logging.Formatter(
                "[%(asctime)s] [%(levelname)s] ::: %(module)s >>> %(message)s"
            )
            stream_handler = logging.StreamHandler(sys.stdout)
            stream_handler.setFormatter(stream_formatter)
            __logger.addHandler(stream_handler)

        return __logger
