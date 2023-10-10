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
        ##self.websites = ["https://terraloteos-app.com/rest", "https://beego.com.ar/api"]
        self.last_response = ""

    @commands.slash_command()
    async def website_add(self, ctx, url: discord.Option(str, description="URL del sitio web a monitorear", required=True)):
        # Verifica si el sitio web ya está en la base de datos
        existing_website = Website.objects.find(filter=f"url = '{url}'")
        
        if existing_website:
            await ctx.respond(f"El sitio web {url} ya está en la lista.")
        else:
            # Agrega el nuevo sitio web a la base de datos
            newWebsite = Website({"url": url})
            newWebsite.save()
            await ctx.respond(f"El sitio web {url} ha sido añadido.")

    @commands.slash_command()
    async def website_delete(self, ctx, url: discord.Option(str, description="URL del sitio web a monitorear", required=True)):
        # Verifica si el sitio web ya está en la base de datos
        existing_website = Website.objects.find(filter=f"url = '{url}'")
        
        if existing_website:
            # Elimina el sitio web de la base de datos
            existing_website.delete()
            await ctx.respond(f"El sitio web {url} ha sido eliminado.")
        else:
            await ctx.respond(f"El sitio web {url} no está en la lista.")
        
   
    @commands.slash_command()
    async def website_status(self, ctx):
        websites = Website.objects.all()
        ##map website and return only url
        websites = map(lambda x: x["url"], websites)

        res = ""
        img_status = 200
        for website in websites:
            url = website
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        if response.status == 200:
                            res += f"{url}: {response.status} OK\n"
                        else:
                            img_status = response.status
                            res += f"{url}: {response.status} ERROR\n"
                        
            except Exception as e:
                res += f"{url}: NO STATUS ERROR\n"
        embed=discord.Embed(title="STATUS", description=res, color=0x00ccff)
        embed.set_image(url=f"https://http.cat/{img_status}.jpg")
        await ctx.respond(embed=embed)

    @tasks.loop(minutes=2)
    async def background_tasks(self):
        websites = Website.objects.all()
        ##map website and return only url
        websites = map(lambda x: x["url"], websites)
        res = ""
        img_status = 522
        for website in websites:
            url = website
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        if response.status != 200:
                            res += f"{url}: {response.status} ERROR\n"
                            img_status = response.status
            except Exception as e:
                res += f"{url}: NO STATUS ERROR\n"    

        if(res != ""):
            embed=discord.Embed(title="STATUS", description=res, color=0x00ccff)
            embed.set_image(url=f"https://http.cat/{img_status}.jpg")      
            await self.bot.get_channel(1159503632220295270).send(embed=embed)
            
    @background_tasks.before_loop
    async def background_task_before(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(Websites(bot))