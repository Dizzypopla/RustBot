import os
import asyncio
import discord
from discord.ext import commands
from discord.ui import Button, View
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

GUILD_ID = int(os.getenv("GUILD_ID"))
TICKET_CATEGORY_ID = int(os.getenv("TICKET_CATEGORY_ID"))
ADMIN_ROLE_ID = int(os.getenv("ADMIN_ROLE_ID"))
ACCEPT_ROLE_ID = int(os.getenv("ACCEPT_ROLE_ID"))

ACCEPT_MANAGE_ROLES = [
    ADMIN_ROLE_ID,
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

def gif_file_if_exists():
    path = os.path.join(os.path.dirname(__file__), GIF_PATH)
    return path if os.path.exists(path) else None

# === Persistent View ===
class ApplicationView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Button(label="📩 Подати заявку", style=discord.ButtonStyle.primary, custom_id="apply_button"))

    @discord.ui.button(label="📩 Подати заявку", style=discord.ButtonStyle.primary, custom_id="apply_button")
    async def apply_callback(self, interaction: discord.Interaction, button: Button):
        guild = interaction.guild
        category = guild.get_channel(TICKET_CATEGORY_ID)
        if not category:
            return await interaction.response.send_message("❌ Категорія для заявок не знайдена.", ephemeral=True)

        safe_name = interaction.user.name.lower().replace(" ", "-")
        existing = discord.utils.get(guild.text_channels, name=f"заявка-{safe_name}")
        if existing:
            return await interaction.response.send_message(f"❗ У вас вже є заявка: {existing.mention}", ephemeral=True)

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

        gif_path = gif_file_if_exists()
        if gif_path:
            file = discord.File(gif_path, filename="standard_9.gif")
            embed_ticket.set_image(url="attachment://standard_9.gif")
            await ticket_channel.send(embed=embed_ticket, file=file)
        else:
            await ticket_channel.send(embed=embed_ticket)

        await interaction.response.send_message(f"✅ Заявку створено: {ticket_channel.mention}", ephemeral=True)

@bot.event
async def on_ready():
    bot.add_view(ApplicationView())  # <-- теперь кнопка работает после рестарта
    print(f"✅ Бот запущено як {bot.user}")

@bot.command()
@commands.has_role(ADMIN_ROLE_ID)
async def заявка(ctx):
    embed = discord.Embed(
        title="📩 Подати заявку в клан",
        description="Натисніть кнопку нижче, щоб створити приватний канал для заповнення анкети.\n\n"
                    f"📜 **Анкета:**\n```\n{APPLICATION_TEMPLATE}\n```\n\n"
                    "## ⚙️ Вимоги до кандидатів:\n"
                    "● Від 3 000 годин у Rust\n"
                    "● Вік 16+ (без винятків)\n"
                    "● Від 35 FC (R2)\n"
                    "● Серйозне ставлення до гри\n"
                    "● Активність, командна гра, адекватність",
        color=0x3498db
    )
    embed.set_footer(text="MX Clan Recruitment")

    gif_path = gif_file_if_exists()
    if gif_path:
        file = discord.File(gif_path, filename="standard_9.gif")
        embed.set_image(url="attachment://standard_9.gif")
        await ctx.send(embed=embed, file=file, view=ApplicationView())
    else:
        await ctx.send(embed=embed, view=ApplicationView())

if not TOKEN:
    print("❌ Помилка: Токен не знайдено! Переконайтесь, що DISCORD_TOKEN є в Railway Variables.")
else:
    bot.run(TOKEN)
