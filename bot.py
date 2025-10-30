import os
import asyncio
import discord
from discord.ext import commands
from discord.ui import Button, View
from dotenv import load_dotenv

# === Завантаження токена ===
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# === Налаштування ===
GUILD_ID = 1304564477152202862
TICKET_CATEGORY_ID = 1366447608721178735  # !!! Вкажи справжній ID категорії !!!
ADMIN_ROLE_ID = 1304567009656307735
ACCEPT_ROLE_ID = 1304596188665872384

ACCEPT_MANAGE_ROLES = [
    1304567009656307735,
    1325195635066146858,
    1325197616086253688,
    1304596329431044187
]

GIF_PATH = "standard_9.gif"

# === Інтенти ===
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# === Стан тикетів ===
tickets_open = True

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

# === Подія готовності ===
@bot.event
async def on_ready():
    print(f"✅ Бот запущено як {bot.user}")

# === Кнопка заявки ===
@bot.command()
@commands.has_role(ADMIN_ROLE_ID)
async def заявка(ctx):
    description = (
        "Натисніть кнопку нижче, щоб створити приватний канал для заповнення анкети.\n\n"
        "📜 **Анкета:**\n"
        f"```\n{APPLICATION_TEMPLATE}\n```\n\n"
        "## ⚙️ Вимоги до кандидатів:\n"
        "● Від 3 000 годин у Rust\n"
        "● Вік 16+ (без винятків)\n"
        "● Від 35 FC (R2)\n"
        "● Серйозне ставлення до гри\n"
        "● Активність, командна гра, адекватність"
    )

    embed = discord.Embed(title="📩 Подати заявку в клан", description=description, color=0x3498db)
    embed.set_footer(text="MX Clan Recruitment")

    apply_button = Button(label="📩 Подати заявку", style=discord.ButtonStyle.primary)

    async def apply_callback(interaction: discord.Interaction):
        global tickets_open

        if not tickets_open:
            try:
                await interaction.user.send("❌ Набір до клану наразі закрито. Спробуйте пізніше.")
            except:
                pass
            await interaction.response.send_message("❌ Набір закрито. Перевірте ваші особисті повідомлення.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True, thinking=True)

        guild = interaction.guild
        category = guild.get_channel(TICKET_CATEGORY_ID)
        if category is None:
            await interaction.followup.send("❌ Категорію не знайдено.", ephemeral=True)
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

        await ticket_channel.send(embed=embed_ticket)
        await interaction.followup.send(f"✅ Заявку створено: {ticket_channel.mention}", ephemeral=True)

    apply_button.callback = apply_callback
    view = View()
    view.add_item(apply_button)

    await ctx.send(embed=embed, view=view)

# === Команди керування ===
@bot.command()
@commands.has_role(ADMIN_ROLE_ID)
async def закрыто(ctx):
    global tickets_open
    tickets_open = False
    await ctx.send("🔒 Тикети закрито. Нові заявки створювати неможливо.")

@bot.command()
@commands.has_role(ADMIN_ROLE_ID)
async def открыто(ctx):
    global tickets_open
    tickets_open = True
    await ctx.send("✅ Тикети відкрито. Користувачі можуть подавати заявки.")

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
