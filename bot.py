import os
import asyncio
import discord
from discord.ext import commands
from discord.ui import Button, View
from dotenv import load_dotenv

# === Завантаження токена ===
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# === ID ===
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

# === GIF ===
GIF_PATH = "standard_9.gif"

# === ІНТЕНТИ ===
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# === СТАН ТИКЕТІВ ===
tickets_open = True

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

# === ОПИС КЛАНУ ===
CLAN_DESCRIPTION = """
💥 **Ласкаво просимо до «𝗠𝗫» — елітного клану для справжніх гравців!** 💥

Ми — команда, яка не просто грає, а *живе* своєю грою! Кожен із нас прагне досягти максимальних результатів і підтримувати найвищі стандарти гри.

**🔹 Ми шукаємо саме тебе, якщо ти:**
- Вік: **від 16 років**
- Години в Rust: **3000+**
- Кілі на R2 FC: **35+ стабільних**
- Серйозне ставлення до гри
- Активність, потужний ПК, стабільний FPS
- Командна гра без токсичності

**⚡ Що ти отримаєш:**
🔥 Високий онлайн  
🏆 Досвідчені гравці  
🚫 Без токсичності  
🎧 Зручний Discord  

Приєднуйся вже зараз — шанс не чекає! 💪
"""

# === Перевірка GIF ===
def gif_file_if_exists():
    path = os.path.join(os.path.dirname(__file__), GIF_PATH)
    return path if os.path.exists(path) else None


# === КОМАНДА !заявка ===
@bot.command()
@commands.has_role(ADMIN_ROLE_ID)
async def заявка(ctx):
    description = f"{CLAN_DESCRIPTION}\n\n📜 **Анкета:**\n```\n{APPLICATION_TEMPLATE}\n```"

    embed = discord.Embed(title="📩 Подати заявку в клан", description=description, color=0x3498db)
    embed.set_footer(text="MX Clan Recruitment")

    gif_path = gif_file_if_exists()
    file = discord.File(gif_path, filename="standard_9.gif") if gif_path else None
    if gif_path:
        embed.set_image(url="attachment://standard_9.gif")

    button = Button(label="📩 Подати заявку", style=discord.ButtonStyle.primary)

    async def button_callback(interaction: discord.Interaction):
        global tickets_open
        if not tickets_open:
            await interaction.user.send("❌ На даний момент заявки тимчасово закриті. Спробуйте пізніше.")
            await interaction.response.defer()
            return

        guild = interaction.guild
        category = guild.get_channel(TICKET_CATEGORY_ID)

        if not category or category.type != discord.ChannelType.category:
            await interaction.response.send_message("❌ Невірна категорія для заявок!", ephemeral=True)
            return

        existing = discord.utils.get(guild.text_channels, name=f"заявка-{interaction.user.name.lower().replace(' ', '-')}")
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
            name=f"заявка-{interaction.user.name.lower().replace(' ', '-')}",
            category=category,
            overwrites=overwrites
        )

        ticket_embed = discord.Embed(
            title="📝 Ваша заявка",
            description="Скопіюйте шаблон нижче та заповніть усі пункти:\n\n" + APPLICATION_TEMPLATE,
            color=0x2ecc71
        )
        ticket_embed.set_footer(text="Заповніть усі пункти анкети нижче.")
        if gif_path:
            ticket_embed.set_image(url="attachment://standard_9.gif")

        # Кнопки
        accept_btn = Button(label="✅ Прийняти", style=discord.ButtonStyle.success)
        deny_btn = Button(label="❌ Відхилити", style=discord.ButtonStyle.danger)
        close_btn = Button(label="🔒 Закрити тикет", style=discord.ButtonStyle.secondary)

        async def accept_callback(i: discord.Interaction):
            if any(r.id in ACCEPT_MANAGE_ROLES for r in i.user.roles):
                role = guild.get_role(ACCEPT_ROLE_ID)
                if role:
                    await interaction.user.add_roles(role)
                await ticket.send(f"✅ {interaction.user.mention} прийнято до клану!")
            else:
                await i.response.send_message("❌ Немає прав.", ephemeral=True)

        async def deny_callback(i: discord.Interaction):
            if any(r.id in ACCEPT_MANAGE_ROLES for r in i.user.roles):
                await ticket.send(f"❌ {interaction.user.mention}, вашу заявку відхилено.")
            else:
                await i.response.send_message("❌ Немає прав.", ephemeral=True)

        async def close_callback(i: discord.Interaction):
            if any(r.id in ACCEPT_MANAGE_ROLES for r in i.user.roles):
                await i.response.send_message("🔒 Канал буде видалено через 5 секунд.", ephemeral=True)
                await asyncio.sleep(5)
                await ticket.delete()
            else:
                await i.response.send_message("❌ Немає прав.", ephemeral=True)

        accept_btn.callback = accept_callback
        deny_btn.callback = deny_callback
        close_btn.callback = close_callback

        view = View()
        view.add_item(accept_btn)
        view.add_item(deny_btn)
        view.add_item(close_btn)

        if gif_path:
            await ticket.send(embed=ticket_embed, view=view, file=discord.File(gif_path, filename="standard_9.gif"))
        else:
            await ticket.send(embed=ticket_embed, view=view)

        await interaction.response.send_message(f"✅ Заявку створено: {ticket.mention}", ephemeral=True)

    button.callback = button_callback
    view = View()
    view.add_item(button)

    await ctx.send(embed=embed, view=view, file=file if file else None)


# === КОМАНДИ ДЛЯ ВІДКЛЮЧЕННЯ/ВІДКРИТТЯ ТИКЕТІВ ===
@bot.command()
@commands.has_role(ADMIN_ROLE_ID)
async def закрито(ctx):
    global tickets_open
    tickets_open = False
    await ctx.send("🔒 Тикети тепер закриті. Нові заявки подати не можна.")

@bot.command()
@commands.has_role(ADMIN_ROLE_ID)
async def відкрито(ctx):
    global tickets_open
    tickets_open = True
    await ctx.send("✅ Тикети знову відкриті! Користувачі можуть подавати заявки.")


# === Запуск ===
@bot.event
async def on_ready():
    print(f"✅ Бот запущено як {bot.user}")

if not TOKEN:
    print("❌ Помилка: Токен не знайдено! Перевірте Railway Variables.")
else:
    bot.run(TOKEN)
