from utils import token_validation as tval


def test_token_validation():
    real_token = "-"
    fake_token = "this is fake token"
    assert tval.token_validation(real_token)[0]
    assert not tval.token_validation(fake_token)[0]