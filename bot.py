# bot.py
import os
import asyncio
import discord
from discord.ext import commands
from discord.ui import Button, View
from dotenv import load_dotenv
from uuid import uuid4

# load env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# config (поставь свои ID)
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

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

tickets_open = True  # глобальное состояние приёма заявок


# ---- helper: создать discord.File динамически ----
def make_gif_file():
    if os.path.exists(GIF_PATH):
        return discord.File(GIF_PATH, filename="standard_9.gif")
    return None


# ---- команды админа для включения/выключения приёма ----
@bot.command()
@commands.has_role(ADMIN_ROLE_ID)
async def закрыто(ctx):
    global tickets_open
    tickets_open = False
    await ctx.send("🚫 Тикеты временно закрыты. Новые заявки не принимаются.")


@bot.command()
@commands.has_role(ADMIN_ROLE_ID)
async def открыто(ctx):
    global tickets_open
    tickets_open = True
    await ctx.send("✅ Тикеты снова открыты.")


# ---- принудительное закрытие (удаление) тикета админом ----
@bot.command()
@commands.has_role(ADMIN_ROLE_ID)
async def forceclose(ctx, target: str):
    """
    Использование:
    !forceclose <user_id>  - удалит канал заявки пользователя (если есть)
    !forceclose channel    - удалит текущий канал (если это тикет)
    """
    guild = ctx.guild
    if target.lower() == "channel":
        try:
            await ctx.channel.delete(reason=f"Force close by {ctx.author}")
        except Exception as e:
            await ctx.send(f"Ошибка: {e}")
        return

    # пробуем найти по user id
    try:
        uid = int(target)
    except:
        await ctx.send("Укажите ID пользователя или 'channel'.")
        return

    name = f"заявка-{uid}"
    ch = discord.utils.get(guild.text_channels, name=name)
    if ch:
        await ch.delete(reason=f"Force close by {ctx.author}")
        await ctx.send(f"Канал {name} удалён.")
    else:
        await ctx.send("Канал не найден.")


# ---- Команда для отправки главного сообщения с кнопкой (для админов) ----
@bot.command()
@commands.has_role(ADMIN_ROLE_ID)
async def заявка(ctx):
    """Отправляет основное сообщение с кнопкой Подать заявку"""
    global tickets_open

    description = (
        "**💥 Ласкаво просимо до «MX» — елітного клану! 💥**\n\n"
        "🔹 **Вимоги:**\n"
        "• Вік: від 16 років\n"
        "• Години в Rust: 3000+\n"
        "• Кілі на R2 FC: 35+\n"
        "• Серйозне ставлення до гри\n"
        "• Активність, командна гра, адекватність\n\n"
        "Натисніть кнопку нижче, щоб подати заявку 👇"
    )

    embed = discord.Embed(title="📩 Подати заявку до MX", description=description, color=0x2ecc71)
    embed.set_footer(text="MX Clan Recruitment")

    # создаём кнопку с уникальным custom_id (чтобы не было конфликтов)
    apply_button = Button(label="📩 Подати заявку", style=discord.ButtonStyle.primary,
                          custom_id=f"apply_{uuid4().hex}")

    async def apply_callback(interaction: discord.Interaction):
        global tickets_open
        await interaction.response.defer(ephemeral=True, thinking=True)

        if not tickets_open:
            await interaction.followup.send("🚫 На даний момент прийом заявок закритий.", ephemeral=True)
            return

        guild = interaction.guild
        if guild is None:
            await interaction.followup.send("❌ Сервер не найден.", ephemeral=True)
            return

        # убедимся что категория валидная
        category = guild.get_channel(TICKET_CATEGORY_ID)
        if category is None or not isinstance(category, discord.CategoryChannel):
            await interaction.followup.send("❌ Невірна категорія для заявок. Зверніться до адміністрації.", ephemeral=True)
            return

        uid = interaction.user.id
        ch_name = f"заявка-{uid}"
        existing = discord.utils.get(guild.text_channels, name=ch_name)
        if existing:
            await interaction.followup.send(f"❗ У вас вже відкрита заявка: {existing.mention}", ephemeral=True)
            return

        # права
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        for role_id in ACCEPT_MANAGE_ROLES:
            role = guild.get_role(role_id)
            if role:
                overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        # создаём канал
        ticket_channel = await guild.create_text_channel(
            name=ch_name,
            category=category,
            overwrites=overwrites
        )

        # embed с анкетой
        app_text = (
            "**📝 Анкета для заповнення:**\n"
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
        embed_ticket = discord.Embed(title="📋 Ваша заявка", description=app_text, color=0x3498db)
        embed_ticket.set_footer(text="MX Clan Application")

        # добавляем кнопку закрытия тикета в самом канале
        close_btn = Button(label="🔒 Закрити тикет", style=discord.ButtonStyle.secondary,
                           custom_id=f"close_{uuid4().hex}")

        async def close_callback(i: discord.Interaction):
            # разрешаем закрывать админам или тем, кто открыл (owner)
            if any(r.id in ACCEPT_MANAGE_ROLES for r in i.user.roles) or i.user.id == uid:
                await i.response.send_message("🔒 Тикет буде видалено через 3 секунди.", ephemeral=True)
                await asyncio.sleep(3)
                try:
                    await ticket_channel.delete(reason=f"Closed by {i.user}")
                except Exception:
                    pass
            else:
                await i.response.send_message("❌ У вас немає прав для цього.", ephemeral=True)

        close_btn.callback = close_callback
        view_ticket = View()
        view_ticket.add_item(close_btn)

        # Отправляем embed в канал тикета и отдельным образом создаём discord.File (каждый раз новый объект)
        gif_file = make_gif_file()
        if gif_file:
            embed_ticket.set_image(url="attachment://standard_9.gif")
            await ticket_channel.send(embed=embed_ticket, view=view_ticket, file=gif_file)
        else:
            await ticket_channel.send(embed=embed_ticket, view=view_ticket)

        await interaction.followup.send(f"✅ Заявку створено: {ticket_channel.mention}", ephemeral=True)

    apply_button.callback = apply_callback
    view = View()
    view.add_item(apply_button)

    # отправляем главное сообщение; создаём файл отдельно
    gif_file_main = make_gif_file()
    if gif_file_main:
        embed.set_image(url="attachment://standard_9.gif")
        await ctx.send(embed=embed, view=view, file=gif_file_main)
    else:
        await ctx.send(embed=embed, view=view)


# ---- on_ready ----
@bot.event
async def on_ready():
    print(f"✅ Бот запущено як {bot.user}")


if not TOKEN:
    print("❌ Токен не знайдено у DISCORD_TOKEN.")
else:
    bot.run(TOKEN)
