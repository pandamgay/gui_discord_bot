from utils import token_validation as tval
from dotenv import load_dotenv
import os


def test_token_validation():
    load_dotenv()
    real_token = os.environ.get('TOKEN')
    fake_token = "this is fake token"
    assert tval.token_validation(real_token)[0]
    assert not tval.token_validation(fake_token)[0]