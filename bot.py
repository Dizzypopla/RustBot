import discord
from discord.ext import commands
import os

TOKEN = os.getenv("DISCORD_TOKEN")

GUILD_ID = 1304564477152202862
CATEGORY_ID = 1366447608721178735
TICKET_ROLE_ID = 1304596188665872384
ADMIN_ROLES = [1304567009656307735, 1325195635066146858, 1325197616086253688, 1304596329431044187]

tickets_open = True

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


# ----------- ВИД ТИКЕТА -----------
class ApplicationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(label="📩 Подати заявку", style=discord.ButtonStyle.primary, custom_id="apply_button"))

    @discord.ui.button(label="📩 Подати заявку", style=discord.ButtonStyle.primary, custom_id="apply_button")
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        global tickets_open

        if not tickets_open:
            await interaction.response.send_message("❌ Заявки тимчасово закриті! Спробуйте пізніше.", ephemeral=True)
            return

        guild = bot.get_guild(GUILD_ID)
        category = discord.utils.get(guild.categories, id=CATEGORY_ID)
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.get_role(TICKET_ROLE_ID): discord.PermissionOverwrite(read_messages=True, send_messages=True),
        }

        ticket_channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            category=category,
            overwrites=overwrites,
            reason="Створено нову заявку"
        )

        embed2 = discord.Embed(
            title="📋 Заявка до MX Clan",
            description=(
                "Будь ласка, заповни наступну інформацію:\n\n"
                "1️⃣ Вік:\n"
                "2️⃣ Середній онлайн на день:\n"
                "3️⃣ Кількість годин у Rust:\n"
                "4️⃣ Досвід гри в кланах:\n"
                "5️⃣ Скільки стабільно кілів на сервері R2 (мін. 35):\n"
                "6️⃣ Посилання на Steam профіль:\n"
                "7️⃣ Звідки дізнався про клан:\n"
                "8️⃣ Напрям у Rust (білд / PvP / фарм тощо):"
            ),
            color=0x2b2d31
        )
        embed2.set_footer(text="MX Clan Recruitment")

        gif_path = "standard_9.gif"
        file = discord.File(gif_path, filename="image.gif") if os.path.exists(gif_path) else None
        embed2.set_image(url="attachment://image.gif") if file else None

        await ticket_channel.send(
            content=f"👋 {interaction.user.mention}, дякуємо за інтерес! Заповни інформацію нижче 👇",
            embed=embed2,
            file=file if file else None
        )

        await interaction.response.send_message(
            f"✅ Твій тикет створено: {ticket_channel.mention}", ephemeral=True
        )


# ----------- КОМАНДИ -----------
@bot.command(name="заявка")
async def application(ctx):
    embed = discord.Embed(
        title="📨 Подати заявку до MX",
        description=(
            "**💥 Ласкаво просимо до «𝗠𝗫» — елітного клану для справжніх гравців! 💥**\n"
            "Ми — команда, яка не просто грає, а *живе* своєю грою! 💪\n\n"
            "**🔹 Ми шукаємо саме тебе, якщо ти:**\n"
            "• Вік: від 16 років\n"
            "• Години в Rust: 3000+\n"
            "• Кілі на R2 FC: 35+\n"
            "• Серйозне ставлення до гри\n"
            "• Активність, командна гра, адекватність\n\n"
            "**⚡ Що ти отримаєш, приєднавшись до MX?**\n"
            "🔥 Високий онлайн\n"
            "🏆 Досвідчені гравці\n"
            "🚫 Без токсичності\n"
            "🎧 Зручний Discord\n\n"
            "Натисни кнопку нижче, щоб подати заявку 👇"
        ),
        color=0x2b2d31
    )
    embed.set_footer(text="MX Clan Recruitment")

    gif_path = "standard_9.gif"
    file = discord.File(gif_path, filename="image.gif") if os.path.exists(gif_path) else None
    embed.set_image(url="attachment://image.gif") if file else None

    await ctx.send(embed=embed, file=file if file else None, view=ApplicationView())


@bot.command(name="закрыто")
async def close_tickets(ctx):
    global tickets_open
    tickets_open = False
    await ctx.send("❌ Тикети закриті. Нові заявки тимчасово неможливі.")


@bot.command(name="открыто")
async def open_tickets(ctx):
    global tickets_open
    tickets_open = True
    await ctx.send("✅ Тикети відкриті! Можна подавати заявки.")


# ----------- СТАРТ -----------
@bot.event
async def on_ready():
    print(f"✅ Бот запущено як {bot.user}")


bot.run(TOKEN)
