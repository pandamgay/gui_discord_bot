import logging
import discord
from discord.ext import commands
from discord import app_commands
import traceback


class Data_command(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.my_logger = bot.shared_data["LOGGER"]

    # @app_commands.command(name="데이터베이스-갱신", description="DB를 갱신합니다. (무거운 작업이므로 실행에 주의가 필요합니다.)")
    # @app_commands.default_permissions(administrator=True)
    # async def refreshData(self, interaction: discord.Interaction):
    #
    #     shared = self.bot.shared_data
    #     user = f"{interaction.user.display_name}[{interaction.user.id}]"
    #     guild = self.bot.get_guild(shared["GUILD_ID"])
    #     cursor = shared["CURSOR"]
    #     db = shared["DB"]
    #     await interaction.response.defer()
    #     self.my_logger.info(f"DB갱신이 사용됨 - {user}")
    #
    #     # 멤버 목록 가져오기
    #     members = guild.members
    #
    #     # DB 갱신
    #     i = 0
    #     j = 0
    #     k = 0
    #     for member in members:
    #         user = f"{member.display_name}[{member.id}]"
    #         i += 1
    #         try:
    #             cursor.execute(
    #                 f"SELECT COUNT(*) "
    #                 f"FROM users "
    #                 f"WHERE discord_user_id = {member.id}"
    #             ) # 멤버가 DB에 존재하는지 확인
    #             exists = cursor.fetchone()[0]
    #             if exists:
    #                 k += 1
    #                 self.my_logger.debug(f"{user}는 이미 DB에 존재합니다. *** [{i}][{k}]")
    #                 continue
    #             cursor.execute(
    #                 f"INSERT INTO "
    #                 f"users (discord_user_id) "
    #                 f"VALUES ({member.id})"
    #             ) # 멤버 정보 저장
    #             db.commit()
    #             self.my_logger.debug(f"{user}의 정보를 DB에 성공적으로 저장했습니다. *** [{i}]")
    #         except Exception as e:
    #             j += 1
    #             tb = traceback.format_exc()
    #             self.my_logger.error(f"DB에 멤버 정보를 저장하는 중 오류 발생: {tb} *** [{i}][{j}]")
    #             continue
    #     await interaction.followup.send(
    #         f"DB 갱신 완료 - 총 {i}명의 멤버 중 {k}명의 중복, {j}명의 오류 발생\n"
    #         f" 실행시간: {interaction.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
    #     )
    #     self.my_logger.info(f"DB 갱신 완료 - 총 {i}명의 멤버 중 {k}명의 중복, {j}명의 오류 발생")

    @app_commands.command(name="데이터-추가", description="멤버 데이터를 추가합니다.")
    @app_commands.describe(멤버="추가할 멤버를 입력하세요.")
    @app_commands.default_permissions(administrator=True)
    async def addUserData(self, interaction: discord.Interaction, 멤버: discord.Member):

        shared = self.bot.shared_data
        user = f"{interaction.user.display_name}[{interaction.user.id}]"
        guild = self.bot.get_guild(shared["GUILD_ID"])
        cursor = shared["CURSOR"]
        db = shared["DB"]

        try:
            cursor.execute(
                f"SELECT COUNT(*) "
                f"FROM users "
                f"WHERE discord_user_id = {멤버.id}"
            ) # 멤버가 DB에 존재하는지 확인
            exists = cursor.fetchone()[0]
            if exists:
                self.my_logger.debug(f"{user}는 이미 DB에 존재합니다.")
                await interaction.response.send_message("이미 DB에 존재하는 멤버입니다.", ephemeral=True)
                return
            cursor.execute(
                f"INSERT INTO users (discord_user_id) "
                f"VALUES ({멤버.id})"
            ) # 멤버 정보 저장
            db.commit()
            self.my_logger.debug(f"{user}의 정보를 DB에 성공적으로 저장했습니다.")
            await interaction.response.send_message(
                f"{멤버.id}의 데이터를 성공적으로 추가했습니다.", ephemeral=True
            )
        except Exception as e:
            tb = traceback.format_exc()
            self.my_logger.error(f"DB에 멤버 정보를 저장하는 중 오류 발생: {tb}")
            await interaction.response.send_message(
                "멤버 정보를 추가하는 중 오류가 발생했습니다.", ephemeral=True
            )

        self.my_logger.info(f"데이터-추가가 사용됨 - {user}")

    @app_commands.command(name="데이터-삭제", description="멤버 데이터를 삭제합니다.")
    @app_commands.describe(멤버="삭제할 멤버를 입력하세요.")
    @app_commands.default_permissions(administrator=True)
    async def deleteUserData(self, interaction: discord.Interaction, 멤버: discord.Member):

        shared = self.bot.shared_data
        user = f"{interaction.user.display_name}[{interaction.user.id}]"
        guild = self.bot.get_guild(shared["GUILD_ID"])
        cursor = shared["CURSOR"]
        db = shared["DB"]

        # DB에 멤버 정보 삭제
        cursor = shared["CURSOR"]
        try:
            cursor.execute(
                f"DELETE FROM users "
                f"WHERE discord_user_id = {멤버.id};"
            ) # 멤버 정보 삭제
            db.commit()
            self.my_logger.debug(f"{user}의 정보를 DB에 성공적으로 삭제했습니다.")
            await interaction.response.send_message(
                f"{멤버.id}의 데이터를 성공적으로 삭제했습니다.", ephemeral=True
            )
        except Exception as e:
            tb = traceback.format_exc()
            self.my_logger.error(f"DB에 멤버 정보를 삭제하는 중 오류 발생: {tb}")
            await interaction.response.send_message(
                "멤버 정보를 삭제하는 중 오류가 발생했습니다.", ephemeral=True
            )
            return

        self.my_logger.info(f"데이터-삭제가 사용됨 - {user}")

    # @app_commands.command(
    #     name="데이터베이스-검증",
    #     description="DB에 저장된 멤버 정보를 검증하여 유령 데이터를 잡아냅니다. "
    #                 "(무거운 작업이므로 실행에 주의가 필요합니다.)"
    # )
    # @app_commands.default_permissions(administrator=True)
    # async def verifyData(self, interaction: discord.Interaction):
    #
    #     shared = self.bot.shared_data
    #     user = f"{interaction.user.display_name}[{interaction.user.id}]"
    #     guild = self.bot.get_guild(shared["GUILD_ID"])
    #     cursor = shared["CURSOR"]
    #     db = shared["DB"]
    #     await interaction.response.defer()
    #     self.my_logger.info(f"DB검증이 사용됨 - {user}")
    #
    #     # DB에 저장된 멤버 정보 가져오기
    #     try:
    #         cursor.execute(
    #             "SELECT * "
    #             "FROM users;"
    #         ) # 테이블 전체 조회
    #         db_users = cursor.fetchall()
    #     except Exception as e:
    #         tb = traceback.format_exc()
    #         self.my_logger.error(f"DB에서 멤버 정보를 가져오는 중 오류 발생: {tb}")
    #         return
    #
    #     # 멤버 목록 가져오기
    #     members = guild.members
    #
    #     i = 0
    #     j = 0
    #     k = 0
    #     # DB와 서버 멤버 정보 비교
    #     for db_user in db_users:
    #         i += 1
    #         l = 0
    #         for member in members:
    #             l += 1
    #             if db_user[1] == member.id:
    #                 self.my_logger.debug(
    #                     f"DB 데이터 {db_user[0]} - {db_user[1]}는 서버에 존재합니다. *** [{i}]"
    #                 )
    #                 break
    #             elif l == len(members):
    #                 self.my_logger.debug(
    #                     f"DB 데이터 {db_user[0]} - {db_user[1]}는 서버에 존재하지 않습니다. "
    #                     f"삭제 예정입니다. *** [{i}]"
    #                 )
    #                 j += 1
    #                 try:
    #                     cursor.execute(
    #                         f"DELETE FROM users "
    #                         f"WHERE discord_user_id = {db_user[1]};"
    #                     ) # 유령 데이터 삭제
    #                     db.commit()
    #                     self.my_logger.debug(f"DB 멤버 {db_user[1]}의 정보를 성공적으로 삭제했습니다.")
    #                 except Exception as e:
    #                     tb = traceback.format_exc()
    #                     self.my_logger.error(f"DB에서 멤버 정보를 삭제하는 중 오류 발생: {tb}")
    #                     k += 1
    #                     continue
    #             else:
    #                 self.my_logger.debug(
    #                     f"DB 멤버 {db_user[0]} - {db_user[1]}는 서버에 존재하지 않습니다. "
    #                     f"계속 찾는중입니다... *** [{i}][{l}]"
    #                 )
    #     await interaction.followup.send(
    #         f"DB 검증 완료 - 총 {i}개의 데이터 중 {k}개의 오류발생, "
    #         f"{j}개의 유령 데이터가 삭제되었습니다.\n"
    #         f" 실행시간: {interaction.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
    #     )
    #     self.my_logger.info(f"DB 검증 완료 - 총 {i}개의 데이터 중 {k}개의 오류발생, {j}개의 유령 데이터가 삭제되었습니다.")


async def setup(bot):
    self = Data_command(bot)
    await bot.add_cog(Data_command(bot))
    self.my_logger.debug("data_command cog가 성공적으로 로드되었습니다.")
