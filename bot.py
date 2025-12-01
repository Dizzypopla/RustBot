import discord
from discord.ext import commands
import os
import re
import asyncio
from datetime import datetime, timedelta
from io import BytesIO  # Для работы с байтами GIF

TOKEN = os.getenv("DISCORD_TOKEN")

GUILD_ID = 1304564477152202862
CATEGORY_ID = 1366447608721178735
TICKET_ROLE_ID = 1304596188665872384
ADMIN_ROLES = [1304567009656307735, 1325195635066146858, 1325197616086253688, 1304596329431044187]

DENIED_ROLE = 1437500019598033117
RECRUIT_CHANNEL = 1440740120562237450

tickets_open = True
cooldowns = {}

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ---- GIF ----
def load_gif():
    gif_path = "standard_9.gif"
    if not os.path.exists(gif_path):
        return None, None
    # Читаем байты и оборачиваем в BytesIO
    with open(gif_path, "rb") as f:
        data = f.read()
    file = discord.File(fp=BytesIO(data), filename="image.gif")
    return file, "attachment://image.gif"

# ----------- МОДАЛ НА ВІДХИЛЕННЯ ЗАЯВКИ ----------- 
class DenyModal(discord.ui.Modal):
    def __init__(self, user, channel):
        super().__init__(title="Відхилення заявки")
        self.user = user
        self.channel = channel

        self.reason = discord.ui.TextInput(
            label="Причина відхилення",
            placeholder="Вкажіть причину...",
            max_length=300
        )
        self.add_item(self.reason)

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        member = guild.get_member(self.user.id)

        try:
            await member.send(f"❌ Ваша заявка була відхилена.\n**Причина:** {self.reason.value}")
        except:
            pass

        role = guild.get_role(DENIED_ROLE)
        if role:
            await member.add_roles(role)

        await self.channel.send(
            f"🔴 Заявка від користувача {member.mention} була **відхилена**.\n"
            f"**Причина:** {self.reason.value}"
        )

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
        }
        for rid in ADMIN_ROLES:
            role = guild.get_role(rid)
            overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        await self.channel.edit(overwrites=overwrites)
        await interaction.response.send_message("Заявку відхилено.", ephemeral=True)

# ----------- КНОПКА ВІДХИЛЕННЯ ----------- 
class DenyButton(discord.ui.View):
    def __init__(self, user):
        super().__init__(timeout=None)
        self.user = user

    @discord.ui.button(label="❌ Відхилити заявку", style=discord.ButtonStyle.danger, custom_id="deny_ticket")
    async def deny(self, interaction: discord.Interaction, button):
        if not any(role.id in ADMIN_ROLES for role in interaction.user.roles):
            return await interaction.response.send_message("У вас немає прав!", ephemeral=True)

        modal = DenyModal(self.user, interaction.channel)
        await interaction.response.send_modal(modal)

# ----------- СТВОРЕННЯ ТІКЕТУ ----------- 
class ApplicationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📩 Подати заявку", style=discord.ButtonStyle.primary, custom_id="apply_button")
    async def button_callback(self, interaction: discord.Interaction, button):
        global tickets_open

        if not tickets_open:
            await interaction.response.send_message("❌ Заявки закриті.", ephemeral=True)
            return

        guild = interaction.guild
        category = guild.get_channel(CATEGORY_ID)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.get_role(TICKET_ROLE_ID): discord.PermissionOverwrite(read_messages=True, send_messages=True),
        }

        ticket_channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            category=category,
            overwrites=overwrites
        )

        embed2 = discord.Embed(
            title="📋 Заявка до MX Clan",
            description=(
                "Будь ласка, заповни наступну інформацію:\n\n"
                "1️⃣ Вік:\n"
                "2️⃣ Середній онлайн на день:\n"
                "3️⃣ Кількість годин у Rust:\n"
                "4️⃣ Досвід гри в кланах:\n"
                "5️⃣ Кілі на сервері R2 (мін. 45):\n"
                "6️⃣ Посилання на Steam профіль:\n"
                "7️⃣ Звідки дізнався про клан:\n"
                "8️⃣ Напрям у Rust (білд / PvP / фарм тощо):"
            ),
            color=0x2b2d31
        )
        embed2.set_footer(text="MX Clan Recruitment")

        file, url = load_gif()
        if file:
            embed2.set_image(url=url)

        await ticket_channel.send(
            content=f"{interaction.user.mention}, заповни форму нижче 👇",
            embed=embed2,
            file=file,
            view=DenyButton(interaction.user)
        )

        await interaction.response.send_message(
            f"✅ Твій тікет створено: {ticket_channel.mention}", ephemeral=True
        )

# ----------- !ЗАЯВКА ----------- 
@bot.command(name="заявка")
async def application(ctx):
    embed = discord.Embed(
        title="📨 Подати заявку до MX",
        description=(
            "**🔹 Ми шукаємо саме тебе, якщо ти:**\n"
            "• Вік: від 16 років\n"
            "• Години в Rust: 3000+\n"
            "• Кілі на R2 FC: 45+\n"
            "• Активність: 8+ годин на добу\n"
            "• Можливість купувати VIP (10$ +)\n"
            "• Серйозне ставлення до гри\n"
            "• Активність, командна гра, адекватність\n\n"

            "**⚡ Що ти отримаєш, приєднавшись до MX?**\n"
            "🔥 Високий онлайн\n"
            "🏆 Досвідчені гравці\n"
            "🚫 Без токсичності\n"
            "🎧 Зручний Discord\n"
            "💣 Масштабні рейди\n\n"
            "Натисни кнопку нижче, щоб подати заявку 👇"
        ),
        color=0x2b2d31
    )

    file, url = load_gif()
    if file:
        embed.set_image(url=url)

    await ctx.send(embed=embed, file=file, view=ApplicationView())

# ----------- !НАБІР ----------- 
class RecruitModal(discord.ui.Modal, title="Оголошення про набір"):
    name = discord.ui.TextInput(label="Назва клану", max_length=100)
    desc = discord.ui.TextInput(label="Опис", style=discord.TextStyle.paragraph, max_length=2000)

    def __init__(self, user):
        super().__init__()
        self.user = user

    async def on_submit(self, interaction: discord.Interaction):
        user_id = self.user.id

        if user_id in cooldowns and cooldowns[user_id] > datetime.now():
            remain = cooldowns[user_id] - datetime.now()
            return await interaction.response.send_message(
                f"⏳ Ви зможете надіслати оголошення через {remain.seconds // 3600} год.",
                ephemeral=True
            )

        if re.search(r"https?://|www\.|discord\.gg", str(self.desc)):
            cooldowns[user_id] = datetime.now() + timedelta(hours=24)
            try:
                await self.user.send("⚠ Ви порушили правила — лінки заборонені. КД 24 г.")
            except:
                pass
            return await interaction.response.send_message("❌ Лінки заборонені.", ephemeral=True)

        channel = interaction.guild.get_channel(RECRUIT_CHANNEL)

        embed = discord.Embed(
            title=f"📢 Набір у клан: {self.name.value}",
            description=self.desc.value,
            color=0x2b2d31
        )
        embed.set_footer(text=f"Автор: {self.user}")
        embed.set_thumbnail(url=self.user.display_avatar.url)

        await channel.send(content=f"👤 {self.user.mention}", embed=embed)
        cooldowns[user_id] = datetime.now() + timedelta(hours=24)
        await interaction.response.send_message("✅ Оголошення надіслано!", ephemeral=True)

class RecruitView(discord.ui.View):
    @discord.ui.button(label="📝 Опублікувати оголошення", style=discord.ButtonStyle.primary)
    async def open(self, interaction: discord.Interaction, button):
        modal = RecruitModal(interaction.user)
        await interaction.response.send_modal(modal)

@bot.command(name="набір")
async def recruit(ctx):
    embed = discord.Embed(
        title="📢 Набір до кланів",
        description=(
            "Хочеш знайти гравців до свого клану?\n"
            "Натисни кнопку нижче, щоб опублікувати оголошення!\n\n"
            "📋 **Правила:**\n"
            "• 1 раз на 24 години\n"
            "• До 2000 символів\n"
            "• Заборонені будь-які посилання"
        ),
        color=0x2b2d31
    )
    await ctx.send(embed=embed, view=RecruitView())

# ----------- СТАРТ ----------- 
@bot.event
async def on_ready():
    print(f"✅ Бот запущено як {bot.user}")

bot.run(TOKEN)