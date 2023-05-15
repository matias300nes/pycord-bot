from discord.ext import commands
import discord
from discord.ui import Select, Button, Modal, InputText, View


class HorariosView(discord.ui.View):
    current_day = ""
    current_user = ""
    base = []
    options1 = [
        discord.SelectOption(label="8:00"),
        discord.SelectOption(label="8:30"),
        discord.SelectOption(label="9:00")
    ]

    options2 = [
        discord.SelectOption(label="8:00"),
        discord.SelectOption(label="8:30"),
        discord.SelectOption(label="9:00")
    ]

    async def button_callback(self, button, interaction):
        self.current_day = button.label
        self.current_user = str(interaction.user)
        saved = None
        for item in self.base:
            if item["user"] == self.current_user and item[
                    "dia"] == self.current_day:
                saved = item

        button.style = discord.ButtonStyle.primary
        for child in self.children:
            if "button" in child.custom_id and child.custom_id != button.custom_id:
                child.style = discord.ButtonStyle.secondary

            if "button" not in child.custom_id:
                for option in child.options:
                    option.default = False

            if saved is not None:
                if "desde" in child.custom_id and saved["entrada"] is not None:
                    for option in child.options:
                        if option.label == saved["entrada"]:
                            option.default = True
                if "hasta" in child.custom_id and saved["salida"] is not None:
                    for option in child.options:
                        if option.label == saved["salida"]:
                            option.default = True
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label="Lun", custom_id="button-1", row=0)
    async def button_1_callback(self, button, interaction):
        await self.button_callback(button, interaction)

    @discord.ui.button(label="Mar", custom_id="button-2", row=0)
    async def button_2_callback(self, button, interaction):
        await self.button_callback(button, interaction)

    @discord.ui.button(label="Mie", custom_id="button-3", row=0)
    async def button_3_callback(self, button, interaction):
        await self.button_callback(button, interaction)

    @discord.ui.button(label="Jue", custom_id="button-4", row=0)
    async def button_4_callback(self, button, interaction):
        await self.button_callback(button, interaction)

    @discord.ui.button(label="Vie", custom_id="button-5", row=0)
    async def button_5_callback(self, button, interaction):
        await self.button_callback(button, interaction)

    @discord.ui.select(custom_id="desde",
                       placeholder="Entrada",
                       options=options1)
    async def select_6_callback(self, select, interaction):
        saved = None
        for item in self.base:
            if item["user"] == self.current_user and item[
                    "dia"] == self.current_day:
                saved = item
                item["entrada"] = select.values[0]

        if saved is None:
            self.base.append({
                "user": self.current_user,
                "dia": self.current_day,
                "entrada": select.values[0],
                "salida": None
            })
        await interaction.response.defer()

    @discord.ui.select(custom_id="hasta",
                       placeholder="Salida",
                       options=options2)
    async def select_7_callback(self, select, interaction):
        saved = None
        for item in self.base:
            if item["user"] == self.current_user and item[
                    "dia"] == self.current_day:
                saved = item
                item["salida"] = select.values[0]

        if saved is None:
            self.base.append({
                "user": self.current_user,
                "dia": self.current_day,
                "entrada": None,
                "salida": select.values[0]
            })
        await interaction.response.defer()


class Horarios(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command()
    async def horarios_edit(self, ctx):
        await ctx.respond("Editar horarios", view=HorariosView())


def setup(bot):
    bot.add_cog(Horarios(bot))
