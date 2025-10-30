import os
import asyncio
import discord
from discord.ext import commands
from discord.ui import Button, View
from dotenv import load_dotenv

# === Загружаем токен ===
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# === НАСТРОЙКИ ===
GUILD_ID = 1304564477152202862
TICKET_CATEGORY_ID = 1366447608721178735
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

tickets_open = True  # глобальная переменная для состояния тикетов

# === Проверка наличия GIF ===
def gif_file_if_exists():
    path = os.path.join(os.path.dirname(__file__), GIF_PATH)
    return path if os.path.exists(path) else None

# === Команды для админов ===
@bot.command()
@commands.has_role(ADMIN_ROLE_ID)
async def закрыто(ctx):
    global tickets_open
    tickets_open = False
    await ctx.send("🚫 Тикеты временно закрыты. Новые заявки создать нельзя.")

@bot.command()
@commands.has_role(ADMIN_ROLE_ID)
async def открыто(ctx):
    global tickets_open
    tickets_open = True
    await ctx.send("✅ Тикеты снова открыты. Можно подавать заявки.")

# === Команда !заявка ===
@bot.command()
@commands.has_role(ADMIN_ROLE_ID)
async def заявка(ctx):
    description = (
        "**💥 Ласкаво просимо до «𝗠𝗫» — елітного клану для справжніх гравців! 💥**\n"
        "Ми — команда, яка не просто грає, а *живе* своєю грою! 💪\n\n"
        "**🔹 Ми шукаємо саме тебе, якщо ти:**\n"
        "• Вік: від 16 років\n"
        "• Години в Rust: 3000+\n"
        "• Кілі на R2 FC: 35+\n"
        "• Серйозне ставлення до гри\n"
        "• Активність, командна гра, адекватність\n\n"
        "**⚡ Що ти отримаєш, приєднавшись до MX?**\n"
        "🔥 Високий онлайн\n🏆 Досвідчені гравці\n🚫 Без токсичності\n🎧 Зручний Discord\n\n"
        "Натисніть кнопку нижче, щоб подати заявку 👇"
    )

    embed = discord.Embed(title="📩 Подати заявку до MX", description=description, color=0x2ecc71)
    embed.set_footer(text="MX Clan Recruitment")

    gif_path = gif_file_if_exists()
    file = discord.File(gif_path, filename="standard_9.gif") if gif_path else None
    if gif_path:
        embed.set_image(url="attachment://standard_9.gif")

    button = Button(label="📩 Подати заявку", style=discord.ButtonStyle.primary)

    async def button_callback(interaction: discord.Interaction):
        global tickets_open
        if not tickets_open:
            await interaction.response.send_message(
                "🚫 На даний момент прийом заявок закритий. Спробуйте пізніше.",
                ephemeral=True
            )
            return

        guild = interaction.guild
        category = guild.get_channel(TICKET_CATEGORY_ID)
        if category is None:
            await interaction.response.send_message("❌ Категорію не знайдено.", ephemeral=True)
            return

        safe_name = interaction.user.name.lower().replace(" ", "-")
        existing = discord.utils.get(guild.text_channels, name=f"заявка-{safe_name}")
        if existing:
            await interaction.response.send_message(f"❗ У вас вже є заявка: {existing.mention}", ephemeral=True)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        for role_id in ACCEPT_MANAGE_ROLES:
            role = guild.get_role(role_id)
            if role:
                overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        ticket = await guild.create_text_channel(
            name=f"заявка-{safe_name}",
            category=category,
            overwrites=overwrites
        )

        app_text = (
            "**📝 Анкета:**\n"
            "```"
            "1. Ім'я:\n"
            "2. Звідки ви:\n"
            "3. Вік (від 16 років):\n"
            "4. Години в Rust (3000+):\n"
            "5. Кілі на R2 FC (35+):\n"
            "6. Досвід гри в кланах:\n"
            "7. Середній онлайн на день:\n"
            "8. Steam профіль:\n"
            "9. Напрямок у Rust (PVP/білд/фарм):"
            "```\n"
            "Адміністрація перевірить вашу заявку найближчим часом. 🔎"
        )

        embed2 = discord.Embed(title="📋 Ваша заявка", description=app_text, color=0x3498db)
        if gif_path:
            embed2.set_image(url="attachment://standard_9.gif")

        await ticket.send(embed=embed2, file=file if gif_path else None)
        await interaction.response.send_message(f"✅ Заявку створено: {ticket.mention}", ephemeral=True)

    button.callback = button_callback
    view = View()
    view.add_item(button)

    await ctx.send(embed=embed, view=view, file=file if gif_path else None)

# === on_ready ===
@bot.event
async def on_ready():
    print(f"✅ Бот запущено як {bot.user}")

if not TOKEN:
    print("❌ Токен не знайдено у Railway Variables!")
else:
    bot.run(TOKEN)
