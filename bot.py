import os
import asyncio
import discord
from discord.ext import commands
from discord.ui import Button, View
from dotenv import load_dotenv

# === Загрузка токена из .env ===
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# === НАСТРОЙКИ ===
GUILD_ID = 1304564477152202862
TICKET_CATEGORY_ID = 1366447822228164669
ADMIN_ROLE_ID = 1304567009656307735
ACCEPT_ROLE_ID = 1304596188665872384
ACCEPT_MANAGE_ROLES = [
    1304567009656307735,
    1325195635066146858,
    1325197616086253688,
    1304596329431044187
]

GIF_PATH = "standard_9.gif"

# === Интенты ===
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# === Глобальное состояние тикетов ===
tickets_open = True

# === Утилита для GIF ===
def gif_file_if_exists():
    path = os.path.join(os.path.dirname(__file__), GIF_PATH)
    return path if os.path.exists(path) else None

# === Команды управления тикетами ===
@bot.command()
@commands.has_role(ADMIN_ROLE_ID)
async def закрыто(ctx):
    global tickets_open
    tickets_open = False
    await ctx.send("🚫 Тикеты временно закриті. Нові заявки неможливо створити.")

@bot.command()
@commands.has_role(ADMIN_ROLE_ID)
async def открыто(ctx):
    global tickets_open
    tickets_open = True
    await ctx.send("✅ Тикети знову відкриті! Користувачі можуть подавати заявки.")

# === Команда заявки ===
@bot.command()
@commands.has_role(ADMIN_ROLE_ID)
async def заявка(ctx):
    """Відправляє embed з анкетою і кнопкою для створення заявки"""
    global tickets_open
    description = (
        "Натисніть кнопку нижче, щоб створити приватний канал для заповнення анкети.\n\n"
        "## 💥 Ласкаво просимо до «MX» — елітного клану!\n"
        "```\n"
        "1. Ім'я:\n2. Звідки ви:\n3. Вік (від 16 років):\n4. Години в Rust (3000+):\n"
        "5. Кількість кілів на R2 FC (35+):\n6. Досвід гри в кланах:\n7. Середній онлайн:\n8. Steam профіль:\n9. Напрямок (PVP/білд/фарм):\n"
        "```\n\n"
        "⚙️ **Вимоги:**\n"
        "• 3000+ годин у Rust\n• 16+ років\n• 35+ FC R2\n• Серйозне ставлення до гри"
    )

    embed = discord.Embed(title="📩 Подати заявку в MX", description=description, color=0x2ecc71)
    embed.set_footer(text="MX Clan Recruitment")
    gif_path = gif_file_if_exists()
    file = discord.File(gif_path, filename="standard_9.gif") if gif_path else None
    if gif_path:
        embed.set_image(url="attachment://standard_9.gif")

    apply_button = Button(label="📩 Подати заявку", style=discord.ButtonStyle.primary)

    async def apply_callback(interaction: discord.Interaction):
        global tickets_open
        if not tickets_open:
            await interaction.response.send_message(
                "🚫 На даний момент прийом заявок закритий. Спробуйте пізніше.", ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True, thinking=True)
        guild = interaction.guild
        category = guild.get_channel(TICKET_CATEGORY_ID)
        if category is None:
            await interaction.followup.send("❌ Категорія для заявок не знайдена.", ephemeral=True)
            return

        safe_name = interaction.user.name.lower().replace(" ", "-")
        existing = discord.utils.get(guild.text_channels, name=f"заявка-{safe_name}")
        if existing:
            await interaction.followup.send(f"❗ У вас вже є заявка: {existing.mention}", ephemeral=True)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        for role_id in ACCEPT_MANAGE_ROLES:
            role = guild.get_role(role_id)
            if role:
                overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        ticket_channel = await guild.create_text_channel(
            name=f"заявка-{safe_name}",
            category=category,
            overwrites=overwrites
        )

        embed_ticket = discord.Embed(
            title="📝 Ваша заявка",
            description="Скопіюйте шаблон і заповніть усі пункти нижче!",
            color=0x3498db
        )
        if gif_path:
            embed_ticket.set_image(url="attachment://standard_9.gif")

        await ticket_channel.send(embed=embed_ticket, file=file if gif_path else None)
        await interaction.followup.send(f"✅ Заявку створено: {ticket_channel.mention}", ephemeral=True)

    apply_button.callback = apply_callback
    view = View()
    view.add_item(apply_button)

    await ctx.send(embed=embed, view=view, file=file if gif_path else None)

# === Запуск ===
@bot.event
async def on_ready():
    print(f"✅ Бот запущено як {bot.user}")

bot.run(TOKEN)
