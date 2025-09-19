import os
from typing import Tuple
import logging
import traceback
from pathlib import Path

_logger = logging.getLogger("Logger")

def save_token(token: bytes, salt: bytes, path: str = None) -> None:
    '''
    토큰을 파일로 저장하는 함수

    :param token: 저장할 토큰
    :param salt: 저장할 솔트
    :param path: 저장할 경로, None이면 루트/config에 저장
    :return: None
    '''

    if path is None:
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(BASE_DIR, "config")
    else:
        path = Path(path).resolve()
    os.makedirs(path, exist_ok=True)

    try:
        with open(os.path.join(path, "token.bin"), "wb") as f:
            f.write(token)

        with open(os.path.join(path, "salt.bin"), "wb") as f:
            f.write(salt)
    except Exception as e:
        tb = traceback.format_exc()
        _logger.error(f"파일 저장 도중 오류 발생:\n {tb}")
        raise IOError(f"파일 저장 도중 오류 발생:/n {e}")


def load_token(path: str = None) -> Tuple[bytes, bytes]:
    '''
    토큰을 불러오는 함수

    :param path: 불러올 토큰의 config디렉터리의 경로
    :return:
        [0] 불러온 token
        [1] 불러온 salt
    '''

    if path is None:
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(BASE_DIR, "config")
    else:
        path = Path(path).resolve()

    try:
        with open(os.path.join(path, "token.bin"), "rb") as f:
            token = f.read()

        with open(os.path.join(path, "salt.bin"), "rb") as f:
            salt = f.read()
    except FileNotFoundError:
        tb = traceback.format_exc()
        _logger.error(f"파일을 찾을 수 없음:\n {tb}")
        raise FileNotFoundError("저장된 토큰을 찾을 수 없음.")

    return (token, salt)
