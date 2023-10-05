from discord.ext import commands, tasks
import discord
import orm_sqlite
import aiohttp

db = orm_sqlite.Database('bot.db')

class Website(orm_sqlite.Model):  
    id = orm_sqlite.IntegerField(primary_key=True) # auto-increment
    url = orm_sqlite.StringField()

Website.objects.backend = db

if(not Website.objects.table_exists()):
    print("creating table")
    Website.objects.create_table()

class Websites(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.background_tasks.start()
        self.websites = ["https://terraloteos-app.com/rest", "https://beego.com.ar/api"]

    """
     @commands.slash_command()
    async def add_website(ctx, website_url: str):
        print("URL: ",website_url.value)
        # Verifica si el sitio web ya está en la base de datos
        existing_website = Website.objects.find(filter=f"url = '{website_url}'")
        print(existing_website)
        
        if existing_website:
            await ctx.send(f"El sitio web {website_url} ya está en la lista.")
        else:
            # Agrega el nuevo sitio web a la base de datos
            newWebsite = Website({"url": website_url})
            newWebsite.save()
            await ctx.send(f"El sitio web {website_url} ha sido añadido.")
    """
    @commands.slash_command()
    async def website_status(self, ctx):
        res = ""
        for website in self.websites:
            url = website
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=100) as response:
                        res += f"{url}: {response.status}\n"
            except Exception as e:
                res += f"{url}: ERROR\n"
        print("RES: ",res)
        embed=discord.Embed(title="STATUS", description=res, color=0x00ccff)
        await ctx.respond(embed=embed)

    @tasks.loop(minutes=5)
    async def background_tasks(self):
        res = ""
        for website in self.websites:
            url = website
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=100) as response:
                        if response.status != 200:
                            res += f"{url}: {response.status} ERROR\n"
            except Exception as e:
                res += f"{url}: NO STATUS ERROR\n"    

        if(res != ""):
            embed=discord.Embed(title="STATUS", description=res, color=0x00ccff)        
            await self.bot.get_channel(1159503632220295270).send(embed=embed)
            
    @background_tasks.before_loop
    async def background_task_before(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(Websites(bot))