from discord.ext import commands
import discord
from discord.ui import Select, Button, Modal, InputText, View

class ComidaView(discord.ui.View):
    options = [
        discord.SelectOption(
            label="Estandar",
        ),
        discord.SelectOption(
            label="Saludable",
        ),
        discord.SelectOption(
            label="Veggie",
        )
    ]
    @discord.ui.select(
        custom_id="1",
        placeholder="Lunes",
        options=options
    )
    async def select_1_callback(self, select, interaction):
        print(select.values[0])
        ##await interaction.response.edit_message(view = self)
        await interaction.response.defer()

    @discord.ui.select(
        custom_id="2",
        placeholder="Martes",
        options=options
    )
    async def select_2_callback(self, select, interaction):
        print(select.values[0])
        await interaction.response.defer()

    @discord.ui.select(
        custom_id="3",
        placeholder="Miercoles",
        options=options
    )
    async def select_3_callback(self, select, interaction):
        print(select.values[0])
        await interaction.response.defer()

    @discord.ui.select(
        custom_id="4",
        placeholder="Jueves",
        options=options
    )
    async def select_4_callback(self, select, interaction):
        print(select.values[0])
        await interaction.response.defer()

    @discord.ui.select(
        custom_id="5",
        placeholder="Viernes",
        options=options
    )
    async def select_5_callback(self, select, interaction):
        print(select.values[0])
        await interaction.response.defer()


class Comida(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.slash_command()
    async def comida_pedir(self, ctx):
        view = ComidaView()
        await ctx.respond("Comida de la semana!", view=view)

    @commands.slash_command()
    async def comida_ver(self, ctx):
        print("d")


def setup(bot):
    bot.add_cog(Comida(bot))
