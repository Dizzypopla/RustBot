class ApplicationView(discord.ui.View):
    @discord.ui.button(label="📩 Подати заявку", style=discord.ButtonStyle.primary, custom_id="apply_button")
    async def apply_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        global tickets_open
        if not tickets_open:
            try:
                await interaction.user.send("❌ Наразі набір заявок закритий. Будь ласка, спробуй пізніше.")
            except:
                await interaction.response.send_message("❌ Заявки тимчасово закриті.", ephemeral=True)
            return

        guild = interaction.guild
        category = discord.utils.get(guild.categories, id=TICKET_CATEGORY_ID)

        if category is None:
            await interaction.response.send_message("❌ Категорія для заявок не знайдена.", ephemeral=True)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        }

        ticket_channel = await guild.create_text_channel(
            name=f"заявка-{interaction.user.name}",
            category=category,
            overwrites=overwrites
        )

        await interaction.response.send_message(f"✅ Заявку створено: {ticket_channel.mention}", ephemeral=True)
        await ticket_channel.send(f"{interaction.user.mention}, напиши тут свою заявку за зразком!")

@bot.command(name="заявка", aliases=["заявки"])
async def заявка(ctx):
    embed = discord.Embed(
        title="💥 Ласкаво просимо до «𝗠𝗫» — елітного клану для справжніх гравців!",
        description=(
            "Ми — команда, яка не просто грає, а *живе* своєю грою! Кожен із нас прагне досягти максимальних результатів.\n\n"
            "**🔹 Чому «𝗠𝗫»?**\n"
            "У нас ти не тільки виграєш, але й отримаєш неймовірні емоції від кожного моменту! 💪\n\n"
            "**🔑 Ми шукаємо саме тебе, якщо ти:**\n"
            "• **Вік:** від 16 років\n"
            "• **Години в Rust:** 3000+ годин\n"
            "• **Кілі на R2 FC:** 35+ стабільних\n"
            "• **Ставлення до гри:** серйозне і повне занурення у перші дні вайпу\n"
            "• **Активність:** готовність бути на зв'язку та працювати командно\n"
            "• **Технічні вимоги:** потужний ПК і стабільний FPS\n"
            "• **Вміння стріляти:** відмінна точність та знання РТ\n"
            "• **Командна гра:** бажання бути частиною єдиної згуртованої команди\n\n"
            "**⚡ Що ти отримаєш, приєднавшись до MX?**\n"
            "• **🔥 Високий онлайн** — завжди є з ким тренуватись і вигравати.\n"
            "• **🏆 Досвідчені гравці** — ти будеш серед кращих, навчаючись разом із ними.\n"
            "• **🚫 Без токсичності** — тільки підтримка та конструктив.\n"
            "• **🎉 Емоції та задоволення** — кожен день гри — нові враження.\n"
            "• **🎧 Зручний Discord** — все готово для командної гри.\n\n"
            "🌐 **Приєднуйся до нас!** Не зволікай, можливості не чекають!\n"
            "🔗 [Посилання на сервер](#) або пиши в ЛС для деталей!"
        ),
        color=0x2b2d31
    )

    file = discord.File("standard_9.gif", filename="standard_9.gif")
    embed.set_image(url="attachment://standard_9.gif")
    embed.set_footer(text="MX Clan Recruitment")

    await ctx.send(embed=embed, file=file, view=ApplicationView())
