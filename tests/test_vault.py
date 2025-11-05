from utils import token_crypto as tc
from utils import my_logger as ml
from utils import token_vault as tv


def test_token_crypto():
    ml.MyLogger(True, "../logs/").initLogger("Logger")

    cipher_token, salt = tc.encrypt_token("this is token", "password")
    assert b"this is token" == tc.decrypt_token(cipher_token, "password", salt)


def test_token_vault():
    ml.MyLogger(True, "../logs/").initLogger("Logger")

    cipher_token, salt = tc.encrypt_token("this is token", "password")
    tv.save_token(cipher_token, salt, "./config")
    assert cipher_token == tv.load_token("./config")[0]
    assert salt == tv.load_token("./config")[1]


def test_token_vault_and_crypto():
    ml.MyLogger(True, "../logs/").initLogger("Logger")

