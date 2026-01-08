import logging
import discord
from discord.ext import commands
from discord import app_commands
import traceback
from datetime import datetime, timedelta
from discord.ui import Button, View
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger


class AdminCommand(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.scheduler = AsyncIOScheduler()
        self.scheduler.add_job(self.checkWarn, CronTrigger(hour=0, minute=0))  # 매일 12:00 AM 실행
        self.scheduler.start()
        self.my_logger = bot.shared_data["LOGGER"]

    @app_commands.command(name="경고-부여", description="멤버에게 경고를 부여합니다.")
    @app_commands.describe(
        멤버="경고를 부여할 멤버",
        사유="경고 사유",
        기간="경고 기간 (기본값: 30일)"
    )
    @app_commands.default_permissions(administrator=True)
    async def addWarn(self, interaction: discord.Interaction, 멤버: discord.Member, 사유: str, 기간: int = 30):

        shared = self.bot.shared_data
        cursor = shared["CURSOR"]
        db = shared["DB"]
        user = f"{interaction.user.display_name}[{interaction.user.id}]"
        channel = self.bot.get_channel(shared["BEN_LOG_CHANNEL_ID"])
        guild = interaction.guild
        self.my_logger.info(
            f"경고-부여 사용됨 - {user}\n"
            f"멤버: {멤버.display_name}({멤버.id}), 사유: {사유}, 기간: {기간}일"
        )
        role = guild.get_role(1398122039776383038)
        self.my_logger.debug(role)

        if not role:
            self.my_logger.error("경고 역할을 찾을 수 없습니다. 역할 ID를 확인해주세요.")
            await interaction.response.send_message(
                "**[error}** 경고 역할을 찾을 수 없습니다.", ephemeral=True
            )
            return
        try:
            if role in 멤버.roles:
                self.my_logger.warning(f"{멤버.display_name}({멤버.id})는 이미 경고 역할을 가지고 있습니다.")
                await interaction.response.send_message(
                    f"{멤버.mention}님은 이미 경고 역할을 가지고 있습니다.\n"
                    f"2회 경고는 밴 대상입니다. 조치 바랍니다.", ephemeral=True
                )
                return
            await 멤버.add_roles(role)
            self.my_logger.info(f"{멤버.display_name}({멤버.id})에게 경고 역할을 성공적으로 부여했습니다.")
            until = datetime.now() + timedelta(days=기간)
            fomatted_time = until.strftime("%Y-%m-%d")
            cursor.execute(
                f"UPDATE users "
                f"SET warn_until = '{fomatted_time}' "
                f"WHERE discord_user_id = {멤버.id};"
            ) # 경고 기간 저장
            db.commit()
            await channel.send(
                f"# 경고\n"
                f"멤버: {멤버.mention}\n"
                f"사유: {사유}\n"
                f"기간: {기간}일\n"
                f"자세한 사항은 {interaction.user.mention}님에게 문의해주세요."
            )
            await interaction.response.send_message(f"{멤버.mention}님에게 경고를 부여했습니다.")
        except discord.Forbidden:
            self.my_logger.error("경고 역할을 부여할 권한이 없습니다. 권한을 확인해주세요.")
            await interaction.response.send_message(
                "**[error]** 경고 역할을 부여할 권한이 없습니다.", ephemeral=True
            )
            return
        except Exception as e:
            tb = traceback.format_exc()
            self.my_logger.error(f"경고 역할 부여 중 오류 발생: {tb}")
            await interaction.response.send_message(
                "**[error]** 경고 역할 부여 중 오류가 발생했습니다.", ephemeral=True
            )
            return

    async def checkWarn(self):

        shared = self.bot.shared_data
        cursor = shared["CURSOR"]
        db = shared["DB"]
        channel = self.bot.get_channel(shared["BEN_LOG_CHANNEL_ID"])
        guild = self.bot.get_guild(shared["GUILD_ID"])
        role = guild.get_role(1398122039776383038)
        self.my_logger.debug(role)

        members_with_role = [member for member in guild.members if role in member.roles]
        if not members_with_role:
            self.my_logger.info("경고 역할을 가진 멤버가 없습니다.")
            return

        i = 0
        j = 0
        k = 0
        for member in members_with_role:
            try:
                i += 1
                cursor.execute(
                    f"SELECT warn_until "
                    f"FROM users "
                    f"WHERE discord_user_id = {member.id}"
                )  # 경고 기간 조회
                result = cursor.fetchone()[0]
                current_date = datetime.today().date()
                if result and result < str(current_date):
                    k += 1
                    await member.remove_roles(role)
                    self.my_logger.debug(f"{member.display_name}의 경고 역할이 제거되었습니다.")
                    channel.send(f"{member.mention}님의 경고가 만료되어 경고 역할이 제거되었습니다.")
            except Exception as e:
                tb = traceback.format_exc()
                self.my_logger.error(f"경고 확인 중 오류 발생: {tb}")
                j += 1
        self.my_logger.info(
            f"경고 확인 완료 - {i}명의 멤버 중 {k}명의 경고가 만료되었고, "
            f"{j}명의 멤버에서 오류가 발생했습니다."
        )


async def setup(bot):
    self = AdminCommand(bot)
    await bot.add_cog(AdminCommand(bot))
    self.my_logger.debug("AdminCommand cog가 성공적으로 로드되었습니다.")
