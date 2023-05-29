from discord.ext import commands, tasks
import discord
from discord.ui import Select, Button, Modal, InputText, View
import orm_sqlite  
import datetime
import pytz

db = orm_sqlite.Database('bot.db')

class Horario(orm_sqlite.Model):  

    id = orm_sqlite.IntegerField(primary_key=True) # auto-increment
    user = orm_sqlite.StringField()
    dia = orm_sqlite.StringField()
    entrada = orm_sqlite.StringField()
    salida = orm_sqlite.StringField()

Horario.objects.backend = db

if(not Horario.objects.table_exists()):
    print("creating table")
    Horario.objects.create_table()

class HorariosView(discord.ui.View):
    current_day = ""
    current_user = ""
    horario = None
    options = [
        "-","8:00", "9:00", "10:00", "11:00", "12:00", "13:00", "14:00",
        "15:00", "16:00", "17:00", "18:00", "19:00", "20:00", "21:00"
    ]

    options1 = [discord.SelectOption(label=option) for option in options]

    options2 = [discord.SelectOption(label=option) for option in options]

    async def button_callback(self, button, interaction):
        self.current_day = button.label
        self.current_user = str(interaction.user)
        query = Horario.objects.find(filter=f"user = '{self.current_user}' AND dia = '{self.current_day}'")
        if len(query) > 0:
            self.horario = query[0]
        else:
            self.horario = None
        print("HORARIO:",self.horario)

        button.style = discord.ButtonStyle.primary
        for child in self.children:
            if "button" in child.custom_id and child.custom_id != button.custom_id:
                child.style = discord.ButtonStyle.secondary

            if "button" not in child.custom_id:
                for option in child.options:
                    option.default = False

            if self.horario is not None:
                if "desde" in child.custom_id and self.horario["entrada"] is not None:
                    for option in child.options:
                        if option.label == self.horario["entrada"]:
                            option.default = True
                if "hasta" in child.custom_id and self.horario["salida"] is not None:
                    for option in child.options:
                        if option.label == self.horario["salida"]:
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
        if self.horario is None:
            item = {
                "user": self.current_user,
                "dia": self.current_day,
                "entrada": select.values[0],
                "salida": None
            }
            horario = Horario(item)
            horario.save()
            self.horario = horario
        else:
            print("saving entrada")
            self.horario["entrada"] = select.values[0]
            self.horario.update()
        await interaction.response.defer()

    @discord.ui.select(custom_id="hasta",
                       placeholder="Salida",
                       options=options2)
    async def select_7_callback(self, select, interaction):
        if self.horario is None:
            item = {
                "user": self.current_user,
                "dia": self.current_day,
                "entrada": None,
                "salida": select.values[0]
            }
            horario = Horario(item)
            horario.save()
            self.horario = horario
        else:
            print("saving salida")
            self.horario["salida"] = select.values[0]
            self.horario.update()
        await interaction.response.defer()


class Horarios(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.background_tasks.start()

    @commands.slash_command()
    async def horarios_edit(self, ctx):
        await ctx.respond("Editar horarios", view=HorariosView())

    @commands.slash_command()
    async def horarios(self, ctx):
        ##get day of week index
        weekday = datetime.datetime.today().weekday()
        days = [
            {"name": "Lun","text":"Lunes"},
            {"name": "Mar","text":"Martes"},
            {"name": "Mie","text":"Miercoles"},
            {"name": "Jue","text":"Jueves"},
            {"name": "Vie","text":"Viernes"},
            {"name": "Sab","text":"Sabado"},
            {"name": "Dom","text":"Domingo"}
        ]

        ##obtener horarios de todos los usuarios para el dia de hoy
        horarios = Horario.objects.find(filter=f"dia = '{days[weekday]['name']}' and entrada != '-'")

        embed=discord.Embed(title=days[weekday]['text'], description=f"Horarios", color=0x00ccff)
        embed.set_thumbnail(url="https://cdn.icon-icons.com/icons2/1863/PNG/512/schedule_118702.png")
        for horario in horarios:
            embed.add_field(name=horario["user"], value=f"{horario['entrada']} - {horario['salida']}", inline=True)

        horas = ["08", "09", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20"]
        header = "08  09  10  11  12  13  14  15  16  17  18  19  20"
        table = header + "\n"

        for usuario in horarios:
            fila = ""
            tempName = usuario["user"]
            for hora in horas:
                if int(hora) == int(usuario["entrada"].split(":")[0]):
                    fila += "|   "
                elif int(hora) == int(usuario["salida"].split(":")[0]):
                    fila += "|   "
                elif int(hora) > int(usuario["entrada"].split(":")[0]):
                    #agregar 4 letras de tempName y sacarlas de la variable
                    if(tempName == ""):
                        fila += "    "
                    elif(len(tempName) < 4):
                        fila += tempName + " "*(4-len(tempName))
                        tempName = ""
                    else:
                        fila += tempName[0:4]
                        tempName = tempName[4:]
                else:
                    fila += "    "
            table += fila + "\n"

        embed.add_field(name="Tabla horarios", value=f"```{table}```", inline=False)

        embed.set_footer(text="usa /horarios_edit para modificar tus horarios")
        if len(horarios) > 0:
            await ctx.respond(embed=embed)
        else:
            await ctx.respond("No hay horarios para hoy")

    @tasks.loop(minutes=20)
    async def background_tasks(self):
        utc_now = pytz.utc.localize(datetime.datetime.utcnow())
        now = utc_now.astimezone(pytz.timezone("america/Argentina/Cordoba"))
        if int(now.strftime("%H")) == 8 and int(
            now.strftime("%M")) >= 0 and int(now.strftime("%M")) <= 22:
            weekday = datetime.datetime.today().weekday()
            days = [
                {"name": "Lun","text":"Lunes"},
                {"name": "Mar","text":"Martes"},
                {"name": "Mie","text":"Miercoles"},
                {"name": "Jue","text":"Jueves"},
                {"name": "Vie","text":"Viernes"},
                {"name": "Sab","text":"Sabado"},
                {"name": "Dom","text":"Domingo"}
            ]

            ##obtener horarios de todos los usuarios para el dia de hoy
            horarios = Horario.objects.find(filter=f"dia = '{days[weekday]['name']}' and entrada != '-'")

            embed=discord.Embed(title=days[weekday]['text'], description=f"Horarios", color=0x00ccff)
            embed.set_thumbnail(url="https://cdn.icon-icons.com/icons2/1863/PNG/512/schedule_118702.png")
            for horario in horarios:
                embed.add_field(name=horario["user"], value=f"{horario['entrada']} - {horario['salida']}", inline=True)

            horas = ["08", "09", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20"]
            header = "08  09  10  11  12  13  14  15  16  17  18  19  20"
            table = header + "\n"

            for usuario in horarios:
                fila = ""
                tempName = usuario["user"]
                for hora in horas:
                    if int(hora) == int(usuario["entrada"].split(":")[0]):
                        fila += "|   "
                    elif int(hora) == int(usuario["salida"].split(":")[0]):
                        fila += "|   "
                    elif int(hora) > int(usuario["entrada"].split(":")[0]):
                        #agregar 4 letras de tempName y sacarlas de la variable
                        if(tempName == ""):
                            fila += "    "
                        elif(len(tempName) < 4):
                            fila += tempName + " "*(4-len(tempName))
                            tempName = ""
                        else:
                            fila += tempName[0:4]
                            tempName = tempName[4:]
                    else:
                        fila += "    "
                table += fila + "\n"

            embed.add_field(name="Tabla horarios", value=f"```{table}```", inline=False)

            embed.set_footer(text="usa /horarios_edit para modificar tus horarios")
            if len(horarios) > 0:
                await self.bot.get_channel(1100902014021533696).send(embed=embed)

    @background_tasks.before_loop
    async def background_task_before(self):
        await self.bot.wait_until_ready()



def setup(bot):
    bot.add_cog(Horarios(bot))
