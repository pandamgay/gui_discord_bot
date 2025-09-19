from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
from typing import Tuple
import logging
import traceback

_logger = logging.getLogger("Logger")

def encrypt_token(token: str, key: str) -> tuple[bytes, bytes]:
    '''
    토큰을 암호화하는 함수

    :param token: 암호화할 토큰
    :param key: 암호화 키
    :return:
        [0] 암호화된 키
        [1] 솔트
    '''

    key, salt = _str_to_fernet_key(key)
    cipher_suite = Fernet(key)
    token = token.encode("utf-8")

    try:
        cipher_token = cipher_suite.encrypt(token)
    except Exception as e:
        tb = traceback.format_exc()
        _logger.error(f"토큰 암호화 실패:\n{tb}")
        raise ValueError("토큰 암호화 실패")

    _logger.debug("토큰 암호화 완료")

    return (cipher_token, salt)


def decrypt_token(encrypted: bytes, key: str, salt: bytes) -> bytes:
    '''
    토큰을 복호화하는 함수
    
    :param encrypted: 복호화할 토큰
    :param key: 복호화 키
    :param salt: 솔트
    :return: 복호화된 토큰
    '''
    
    key = _str_to_fernet_key(key, salt)[0]
    cipher_suite = Fernet(key)

    try:
        plain_token = cipher_suite.decrypt(encrypted)
    except InvalidToken:
        tb = traceback.format_exc()
        _logger.error(f"올바른 키가 아님:\n{tb}")
        raise ValueError("올바르지 않은 키")
    except Exception:
        tb = traceback.format_exc()
        _logger.error(f"예상치 못한 에러:\n{tb}")
        raise ValueError("토큰 복호화 실패")

    _logger.debug("토큰 복호화 완료")

    return plain_token


def _str_to_fernet_key(text: str, salt: bytes = None) -> Tuple[bytes, bytes]:
    '''
    문자열을 인코딩하여 키로 변경하는 함수

    :param text: 변경할 문자열
    :param salt: 키에 적용할 솔트, None일경우 임의의 솔트 생성
    :return:
        [0] 인코딩된 키
        [1] 생성된 솔트
    '''

    if salt is None:
        salt = os.urandom(16)

    text = text.encode("utf-8")
    key = None

    try:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100_000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(text))
    except Exception as e:
        tb = traceback.format_exc()
        _logger.error(f"키 로드 실패:\n {tb}")

    return (key, salt)
