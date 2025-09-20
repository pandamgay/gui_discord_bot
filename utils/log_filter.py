import logging
import re
import os
import pathlib

from utils import path_helper as ph


def log_filter(level: int, created_module: str, path: pathlib.Path = None) -> str:
    '''
    로그 파일에서 특정 레벨 이상의 로그만 필터링하여 반환하는 함수
    :param level: 필터링할 로그 레벨 (logging 상수 사용.)
    :param created_module: 로그 파일 생성 모듈 이름
    :param path: 로그 파일 경로 None일 경우 기본 경로 사용 (절대경로를 사용해야 합니다.)
    :return: 필터링된 로그 문자열
    '''
    log_level_nums = {
        logging.DEBUG: "[DEBUG]",
        logging.INFO: "[INFO]",
        logging.WARNING: "[WARNING]",
        logging.ERROR: "[ERROR]",
    }
    included_levels = [v for k, v in sorted(log_level_nums.items()) if k >= level]
    log_levels = ["[DEBUG]", "[INFO]", "[WARNING]", "[ERROR]"]
    if path is None:
        log_path = ph.find_dir("gui_discord_bot") / "logs"
    else:
        log_path = path
    pattern = re.compile(rf'^log_(\d{{14}})-{re.escape(created_module)}\.log$')
    matching_files = [f for f in os.listdir(log_path) if pattern.fullmatch(f)]

    if not matching_files:
        raise FileNotFoundError("패턴에 맞는 로그 파일이 없습니다.")

    latest_file = max(matching_files)

    file_path = log_path / latest_file
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.splitlines()
    log = ""
    before_level = False
    for line in lines:
        if any(level in line for level in log_levels):
            if any(level in line for level in included_levels):
                before_level = True
                log += line + "\n"
            else:
                continue
        else:
            if before_level:
                log += line + "\n"
            else:
                continue

    return log
