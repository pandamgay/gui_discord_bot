import asyncio
import sys
import sqlite3

import discord
from discord.ext import commands
from PyQt5.QtCore import *
import os
import traceback
from utils import my_logger as ml
from utils import my_curser as mc


class LumielBot(QObject, commands.Bot):
    signal: pyqtSignal = pyqtSignal(tuple)
    '''
    Tuple[int, str, tuple | None] (type, message, data)
    type: 시그널 타입을 상수로 전달
    message: 시그널 전달 시 추가적인 설명을 전달
    data: 추가적인 데이터가 필요할 경우 전달
    '''

    def __init__(self, **options):
        super().__init__(command_prefix="/", intents=discord.Intents.all(), **options)

        logger = ml.MyLogger(False, "../logs/")
        logger.set_signal(self.signal)
        self.my_logger = logger.initLogger("Lumiel")

        self.signal.connect(self.signal_handler)

        self.bot = self

        self.bot.shared_data = {}

        self.tree.on_error = self.on_app_command_error

        self.channels = {}

    async def on_ready(self):
        activity = discord.Activity(
            name="봇 초기화중...",
            type=discord.ActivityType.playing
        )
        await self.bot.change_presence(activity=activity)

        init_db()
        db = sqlite3.connect("main.db")
        db.row_factory = None
        cursor = db.cursor(factory=mc.MyCursor)

        name_counter = {}

        for guild in self.bot.guilds:
            for channel in guild.channels:
                if isinstance(channel, discord.TextChannel):
                    key = f"# {channel.name} ({guild.name})"
                    count = name_counter.get(key, 0) + 1
                    name_counter[key] = count

                    if count > 1:
                        key = f"# {channel.name}[{count}] ({guild.name})"
                    self.channels[key] = channel.id
            cursor.execute(
                f"INSERT OR IGNORE INTO server (discord_guild_id)"
                f"VALUES ({guild.id});"
            )
            db.commit()

        self.loop = asyncio.get_event_loop()

        self.bot.shared_data = {
            "GUILD_ID": 1383768206635962501,                     # 서버 ID
            "ENTRY_LOG_CHANNEL_ID": 1384501387211313222,         # 입장 로그 채널 ID
            "CHECK_MESSAGE_ID": 1388526152351744061,             # 인증 메시지 ID
            "PEOPLE_COUNT_CHANNEL_ID": 1388573766719901796,      # 인원수 채널 ID
            "event_message_id": int,                             # 이벤트 메시지 ID
            "INVITE_LOG_CHANNEL_ID": 1433423256429400094,        # 초대로그 채널 ID
            "CURSOR": cursor,                                    # DB 커서
            "PROMOTION_LOG_CHANNEL_ID": 1384518652841295912,     # 승급 로그 채널 ID
            "BEN_LOG_CHANNEL_ID": 1398123190999580672,           # 벤 로그 채널 ID
            "DB": db,                                            # DB 연결 객체
            "LOGGER": self.my_logger,                            # 로거
            "invites": {}                                        # 초대 정보
        }

        invites = {}
        for guild in self.bot.guilds:
            invites[guild.id] = {}
            for invite in await guild.invites():
                invites[guild.id] = {invite.code: [invite.uses, invite.inviter.id]}
                '''
                    {int: {str: [int, int]}}
                '''
        self.bot.shared_data["invites"] = invites

        self.my_logger.debug(str(invites))

        # cogs 로드
        await self.load_cogs()

        await self.bot.tree.sync()
        for command in self.bot.tree.get_commands():
            self.my_logger.debug(f"Command: {command.name}")

        # 봇의 상태에서 activity를 제거
        await self.bot.change_presence(activity=None)

        self.my_logger.info(f"{self.bot.user.name} 봇이 성공적으로 초기화되었습니다.")
        self.signal.emit((BOT_INIT_SUCCESS, "봇 초기화 성공"))

    async def load_cogs(self):
        try:
            await self.bot.load_extension("lumiel_bot.cogs.events")
            await self.bot.load_extension("lumiel_bot.cogs.commands.admin_command")
            await self.bot.load_extension("lumiel_bot.cogs.commands.event_command")
            await self.bot.load_extension("lumiel_bot.cogs.commands.data_command")
            await self.bot.load_extension("lumiel_bot.cogs.commands.experience_command")
            await self.bot.load_extension("lumiel_bot.cogs.commands.item_command")
            await self.bot.load_extension("lumiel_bot.cogs.commands.invite_command")
            self.my_logger.debug("cogs가 성공적으로 로드되었습니다.")
        except Exception as e:
            tb = traceback.format_exc()
            self.my_logger.error(f"Cog 로드 중 오류 발생:\n {tb}")
            await self.bot.close()

    def run_lumiel(self, TOKEN):
        if TOKEN:
            self.my_logger.debug("토큰이 성공적으로 로드되었습니다.")
        else:
            self.my_logger.error("토큰이 로드되지 않았습니다.")
            raise EnvironmentError()
        self.bot.run(TOKEN)

    async def send_message(self, message: str, channel_id: int) -> None:
        '''
        채널에 메시지를 보내는 함수
        :param message: 보낼 메시지
        :param channel_id: 보낼 채널 id
        :return: None
        '''
        try:
            channel = self.bot.get_channel(channel_id)
            if channel is None:
                self.signal.emit((CHANNEL_NOT_FOUND, "채널을 찾을 수 없음"))
                self.my_logger.debug("메시지 전송 실패: 채널을 찾을 수 없음")
                return
            await channel.send(message)
        except Exception as e:
            self.signal.emit((SEND_MESSAGE_ERROR, "메시지 전송 도중 오류 발생", (e,)))
            self.my_logger.debug("메시지 전송 실패: 메시지 전송 도중 오류 발생")
        else:
            self.signal.emit((SEND_SUCCESS, "메시지를 성공적으로 전송했습니다."))
            self.my_logger.info("메시지를 성공적으로 전송했습니다.")

    def stop(self):
        asyncio.run_coroutine_threadsafe(self.bot.close(), self.bot.loop)
        self.my_logger.info("봇이 성공적으로 종료되었습니다.")

    async def on_error(self, event, *args, **kwargs):
        exc_type, exc_value, exc_tb = sys.exc_info()
        exc_tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        self.signal.emit((ON_ERROR, "봇 실행 도중 오류 발생", (exc_type, exc_value, exc_tb)))
        self.my_logger.error(f"봇 실행 도중 오류 발생: {exc_value}")

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError) and error.original:
            exc_type = type(error.original)
            exc_value = error.original
            exc_tb = str(error.original.__traceback__)
        else:
            exc_type = type(error)
            exc_value = error
            exc_tb = str(error.__traceback__)

        self.signal.emit((ON_ERROR, "명령어 실행 도중 오류 발생", (exc_type, exc_value, exc_tb)))
        self.my_logger.error(f"명령어 실행 도중 오류 발생: {exc_value}")

    async def on_app_command_error(self, interaction, error):
        exc_type = type(error)
        exc_value = error
        exc_tb = str(getattr(error, "__traceback__", None))

        self.signal.emit((ON_ERROR, f"슬래시 커맨드 오류: {interaction.command}", (exc_type, exc_value, exc_tb)))
        self.my_logger.error(f"명령어 실행 도중 오류 발생: {exc_value}")

    def signal_handler(self, payload):
        if payload[0] == DO_SEND_MESSAGE:
            self.my_logger.debug(f"LumielBot: 시그널 수신됨. message: {payload[1]}")
            asyncio.run_coroutine_threadsafe(
                self.send_message(payload[2][0], payload[2][1]),
                self.loop
            )


def init_db():
    with sqlite3.connect("main.db") as db:
        cursor = db.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS server (
            discord_guild_id BIGINT PRIMARY KEY,
            bot_setting TEXT DEFAULT '{}'
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            discord_user_id BIGINT NOT NULL UNIQUE,
            experience INT NOT NULL DEFAULT 0,
            recent_attendance_date DATE DEFAULT NULL,
            continuous_attendance_date INT DEFAULT 0,
            invite_count INT DEFAULT 0,
            inviter_id INT DEFAULT 0,
            warn_until DATE DEFAULT NULL,
            join_guild INT NOT NULL,
            FOREIGN KEY (join_guild) REFERENCES server(discord_guild_id)
        );
        """)

        db.commit()


BOT_INIT_SUCCESS = 0
ON_ERROR = 1
ON_LOGGING = 30
DO_SEND_MESSAGE = 81
CHANNEL_NOT_FOUND = 84
SEND_MESSAGE_ERROR = 85
SEND_SUCCESS = 80


if __name__ == "__main__":
    bot_instance = LumielBot()
    bot_instance.run("TOKEN")
