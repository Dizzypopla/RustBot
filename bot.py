import discord
from discord.ext import commands
import os

# === Переменные окружения ===
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))
ADMIN_ROLE_IDS = [1304567009656307735, 1325195635066146858, 1325197616086253688, 1304596329431044187]
ACCEPT_ROLE_ID = int(os.getenv("ACCEPT_ROLE_ID"))
TICKET_CATEGORY_ID = int(os.getenv("TICKET_CATEGORY_ID"))

# === Настройки бота ===
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# === Состояние тикетов ===
tickets_open = True

# === GIF ===
GIF_PATH = os.path.join(os.path.dirname(__file__), "standard_9.gif")

def gif_file_if_exists():
    if os.path.exists(GIF_PATH):
        return GIF_PATH
    else:
        print("⚠️ GIF not found at:", GIF_PATH)
        return None


# === View с кнопкой "Подати заявку" ===
class ApplicationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📩 Подати заявку", style=discord.ButtonStyle.primary)
    async def apply_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        global tickets_open
        if not tickets_open:
            await interaction.user.send("❌ На даний момент заявки закриті. Спробуйте пізніше.")
            await interaction.response.send_message("Заявки тимчасово закриті.", ephemeral=True)
            return

        guild = interaction.guild
        category = discord.utils.get(guild.categories, id=TICKET_CATEGORY_ID)
        if category is None:
            await interaction.response.send_message("⚠️ Помилка: категорію для заявок не знайдено.", ephemeral=True)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True, embed_links=True),
        }

        for role_id in ADMIN_ROLE_IDS:
            role = guild.get_role(role_id)
            if role:
                overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

        ticket_channel = await guild.create_text_channel(
            name=f"заявка-{interaction.user.name}",
            category=category,
            overwrites=overwrites
        )

        await ticket_channel.send(
            f"{interaction.user.mention}, дякуємо за заявку! Будь ласка, заповніть форму нижче:\n\n"
            "1. Ваш нікнейм у Steam:\n"
            "2. Вік (від 16 років):\n"
            "3. Дискорд тег:\n"
            "4. Середній онлайн на день:\n"
            "5. Кількість годин у Rust:\n"
            "6. Досвід гри в кланах:\n"
            "7. Скільки стабільно кілів на сервері R2 (мін. 35):\n"
            "8. Посилання на Steam профіль:\n"
            "9. Звідки дізнались про клан:\n"
            "10. Напрям у Rust (білд / PvP / фарм тощо):"
        )
        await interaction.response.send_message(f"✅ Ваша заявка створена: {ticket_channel.mention}", ephemeral=True)


# === Команда !заявка ===
@bot.command()
async def заявка(ctx):
    embed = discord.Embed(
        title="⚙️ Вимоги до кандидатів:",
        description=(
            "● Від 3 000 годин у Rust\n"
            "● Вік 16+ (без винятків)\n"
            "● Від 35 FC (R2)\n"
            "● Серйозне ставлення до гри\n"
            "● Активність, командна гра, адекватність"
        ),
        color=discord.Color.blue()
    )

    gif_path = gif_file_if_exists()
    file = discord.File(gif_path, filename="standard_9.gif") if gif_path else None
    embed.set_image(url="attachment://standard_9.gif" if file else None)
    embed.set_footer(text="MX Clan Recruitment")

    await ctx.send(embed=embed, file=file, view=ApplicationView())


# === Команды управления тикетами ===
@bot.command()
async def закрыто(ctx):
    global tickets_open
    tickets_open = False
    await ctx.send("🚫 Заявки тимчасово **закриті**.")

@bot.command()
async def открыто(ctx):
    global tickets_open
    tickets_open = True
    await ctx.send("✅ Заявки знову **відкриті**!")


# === Запуск бота ===
@bot.event
async def on_ready():
    print(f"✅ Бот запущено як {bot.user}")

bot.run(TOKEN)
