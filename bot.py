import os
import asyncio
import discord
from discord.ext import commands
from discord.ui import Button, View
from dotenv import load_dotenv

# === Загружаем токен из .env ===
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# === НАСТРОЙКИ ===
GUILD_ID = 1304564477152202862
TICKET_CATEGORY_ID = 1366447608721178735
ADMIN_ROLE_ID = 1304567009656307735
ACCEPT_ROLE_ID = 1304596188665872384

ACCEPT_MANAGE_ROLES = [
    1304567009656307735,  # Admin
    1325195635066146858,
    1325197616086253688,
    1304596329431044187
]

GIF_PATH = "standard_9.gif"

# === ІНТЕНТИ ===
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# === АНКЕТА ===
APPLICATION_TEMPLATE = """1. Ім'я:
2. Звідки ви:
3. Вік (від 16 років):
4. Середній онлайн на день:
5. Кількість годин у Rust:
6. Досвід гри в кланах:
7. Скільки стабільно кіллів на сервері R2 (мін. 35):
8. Посилання на Steam профіль:
9. Звідки дізнались про клан:
10. Напрямок у Rust (білд / PvP / фарм тощо):"""

# === ГОТОВНОСТЬ БОТА ===
@bot.event
async def on_ready():
    print(f"✅ Бот запущено як {bot.user}")

# === УТИЛІТА ДЛЯ GIF ===
def gif_file_if_exists():
    path = os.path.join(os.path.dirname(__file__), GIF_PATH)
    return path if os.path.exists(path) else None

# === КОМАНДА ДЛЯ АДМІНІВ: !заявка ===
@bot.command()
@commands.has_role(ADMIN_ROLE_ID)
async def заявка(ctx):
    """Відправляє embed з анкетою і кнопкою для створення заявки"""
    description = (
        "Натисніть кнопку нижче, щоб створити приватний канал для заповнення анкети.\n\n"
        "📜 **Анкета:**\n"
        "```\n"
        f"{APPLICATION_TEMPLATE}\n"
        "```\n\n"
        "## ⚙️ Вимоги до кандидатів:\n\n"
        "## ● Від 3 000 годин у Rust\n"
        "## ● Вік 16+ (без винятків)\n"
        "## ● Від 35 FC (R2)\n"
        "## ● Серйозне ставлення до гри\n"
        "## ● Активність, командна гра, адекватність"
    )

    embed = discord.Embed(title="📩 Подати заявку в клан", description=description, color=0x3498db)
    embed.set_footer(text="MX Clan Recruitment")

    gif_path = gif_file_if_exists()
    files = [discord.File(gif_path, filename="standard_9.gif")] if gif_path else []
    if gif_path:
        embed.set_image(url="attachment://standard_9.gif")

    apply_button = Button(label="📩 Подати заявку", style=discord.ButtonStyle.primary, custom_id="apply_button")

    async def apply_callback(interaction: discord.Interaction):
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
            description="Скопіюйте шаблон нижче та заповніть усі пункти:\n\n" + APPLICATION_TEMPLATE,
            color=0x2ecc71
        )
        embed_ticket.set_footer(text="Заповніть усі пункти анкети нижче.")
        if gif_path:
            embed_ticket.set_image(url="attachment://standard_9.gif")

        applicant = interaction.user

        # === Уникальные custom_id для кнопок ===
        accept_btn = Button(label="✅ Прийняти", style=discord.ButtonStyle.success, custom_id="accept_btn")
        deny_btn = Button(label="❌ Відхилити", style=discord.ButtonStyle.danger, custom_id="deny_btn")
        close_btn = Button(label="🔒 Закрити тикет", style=discord.ButtonStyle.secondary, custom_id="close_btn")

        async def accept_callback(i: discord.Interaction):
            if any(r.id in ACCEPT_MANAGE_ROLES for r in i.user.roles):
                role = ticket_channel.guild.get_role(ACCEPT_ROLE_ID)
                if role:
                    await applicant.add_roles(role)
                await ticket_channel.send(f"✅ {applicant.mention} прийнято до клану! Роль видано.")
            else:
                await i.response.send_message("❌ Немає прав.", ephemeral=True)

        async def deny_callback(i: discord.Interaction):
            if any(r.id in ACCEPT_MANAGE_ROLES for r in i.user.roles):
                await ticket_channel.send(f"❌ {applicant.mention}, вашу заявку відхилено.")
            else:
                await i.response.send_message("❌ Немає прав.", ephemeral=True)

        async def close_callback(i: discord.Interaction):
            if any(r.id in ACCEPT_MANAGE_ROLES for r in i.user.roles):
                await i.response.send_message("🔒 Тикет буде видалено через 5 секунд.", ephemeral=True)
                await asyncio.sleep(5)
                await ticket_channel.delete(reason="Тикет закрито")
            else:
                await i.response.send_message("❌ Немає прав.", ephemeral=True)

        # Привязываем коллбеки
        accept_btn.callback = accept_callback
        deny_btn.callback = deny_callback
        close_btn.callback = close_callback

        view_ticket = View()
        view_ticket.add_item(accept_btn)
        view_ticket.add_item(deny_btn)
        view_ticket.add_item(close_btn)

        if gif_path:
            await ticket_channel.send(embed=embed_ticket, view=view_ticket, file=discord.File(gif_path, filename="standard_9.gif"))
        else:
            await ticket_channel.send(embed=embed_ticket, view=view_ticket)

        await interaction.followup.send(f"✅ Заявку створено: {ticket_channel.mention}", ephemeral=True)

    apply_button.callback = apply_callback
    view = View()
    view.add_item(apply_button)

    await ctx.send(embed=embed, view=view, files=files if files else None)

# === Обробка помилок ===
@заявка.error
async def заявка_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("❌ Цю команду можуть використовувати лише адміністратори.")
    else:
        await ctx.send(f"⚠️ Помилка: {error}")

# === Запуск ===
if not TOKEN:
    print("❌ Помилка: Токен не знайдено! Переконайтесь, що DISCORD_TOKEN є в Railway Variables.")
else:
    bot.run(TOKEN)
