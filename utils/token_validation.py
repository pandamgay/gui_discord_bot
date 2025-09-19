import asyncio
import logging
import traceback
from typing import Tuple, Optional

import discord

_logger = logging.getLogger("Logger")


async def _token_check(token: str) -> Tuple[bool, Optional[str]]:
    '''
    토큰 유효성을 검사하는 함수

    :param token: 검사할 토큰
    :return:
        [0] 토큰의 유효 여부
        [1] 예상치 못한 예외 발생 시 반환할 traceback
    '''

    intents = discord.Intents.none()
    client = discord.Client(intents=intents)

    try:
        await client.http.static_login(token.strip())
        return (True, None)
    except discord.LoginFailure as e:
        _logger.warning(f"잘못된 토큰")
        return (False, None)
    except Exception as e:
        tb = traceback.format_exc()
        _logger.error(f"토큰 유효성 검사 도중 예외 발생:\n{tb}")
        return (False, tb)
    finally:
        await client.close()


def token_validation(token: str) -> Tuple[bool, Optional[str]]:
    return asyncio.run(_token_check(token))
