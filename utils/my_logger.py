import logging
import sys
from datetime import datetime
import os
import inspect

from PyQt5.QtCore import *

from lumiel_bot import main as lumiel


class MyLogger():

    def __init__(self, is_stream: bool, path: str):
        self.class_name = self.__class__.__name__
        self.log_path = path
        os.makedirs("logs", exist_ok=True)
        self.is_stream = is_stream
        self.created_module = inspect.stack()[1].frame.f_globals["__name__"]

        self.signal: pyqtSignal = None
        self.signal_handler: SignalHandler = None

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
        if self.signal_handler is not None:
            __logger.addHandler(self.signal_handler)

        if self.is_stream:
            stream_formatter = logging.Formatter(
                "[%(asctime)s] [%(levelname)s] ::: %(module)s >>> %(message)s"
            )
            stream_handler = OverwriteHandler(sys.stdout)
            stream_handler.setFormatter(stream_formatter)
            __logger.addHandler(stream_handler)

        return __logger

    def set_signal(self, signal: pyqtSignal):
        '''signal추가 시 반드시 initLogger 이전에 호출할 것'''
        self.signal = signal
        self.signal_handler = SignalHandler(signal)


class SignalHandler(logging.Handler):

    def __init__(self, signal: pyqtSignal):
        super().__init__()
        self.signal = signal
        self.formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] ::: %(module)s.%(funcName)s:%(lineno)d >>> %(message)s"
        )

    def emit(self, record):
        formatted_message = self.formatter.format(record)
        self.signal.emit((lumiel.ON_LOGGING, "로그 발생함.", (formatted_message,)))


class OverwriteHandler(logging.StreamHandler):
    before_msg = ""
    before_msg_count = 1

    def emit(self, record):
        try:
            msg = record.getMessage()
            if self.before_msg == msg:
                self.before_msg_count += 1
                self.stream.write(f"\r{self.format(record)} [{self.before_msg_count}]")
            else:
                self.before_msg = msg
                self.before_msg_count = 1
                self.stream.write("\n" + self.format(record))
            self.stream.flush()
        except Exception:
            self.handleError(record)
