import threading
import time
from itertools import cycle
import discord
from discord.ext import commands
from discord.ext.commands import has_permissions

from webrequests import DataIO, Config

intents = discord.Intents().all()
Client = commands.Bot(command_prefix="$", intents=intents)

status = cycle(['status1', 'status2', '...'])

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='.', intents=intents, help_command=None)
bot.owner_id = 933369720361586699
botdata = {}
pingcooldown = []

status = "with the Ocean"
api_key_dev = ""
api_key_stable = ""
updatesuccess = True


def syncdata(bot):
    global botdata

    listener = Config(bot).listener(port=1999)

    while True:
        try:
            conn = listener.accept()
            data = conn.recv()

            if data == "close":
                listener.close()
                break

            botdata = data
        except:
            pass


@bot.event
async def on_ready():
    global botdata
    global updatesuccess

    print("Bot online")

    dataio = DataIO(bot)
    botdata = dataio.createconfig("other")

    for guild in bot.guilds:
        botdata[dataio.gethash(bytes(str(guild.id), "utf-8"))] = dataio.createconfig("server")

    botdata = dataio.loadconfig()

    # this line automatically makes the bot go into "playing a game" mode.
    await bot.change_presence(activity=discord.Game(f"{status}"))


class restricted(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Users with the ctx.author.id permissions are the only people"
                                  " who have access to these commands.")
    async def admin(self, ctx, module, value=None, *, reason=None):
        global botdata
        # If this line is suspended, Admin Commands will be able to be accessed by anyone with no regulation.
        if ctx.author.id == bot.owner_id:
            if module == "stats":
                ping = round(self.bot.latency * 1000)
                servers = len(self.bot.guilds)

                embed = discord.Embed(title="Bot statistics", description="Processing...",
                                      color=discord.Colour.dark_blue())

                start = time.perf_counter()
                msg = await ctx.send(embed=embed)
                end = time.perf_counter()
                time.sleep(1)

                total = ((end - start) * 1000) - ping

                embed = discord.Embed(title="Bot statistics", color=discord.Colour.dark_blue())
                embed.add_field(name="Connection Latency", value=f"{ping}ms")
                embed.add_field(name="API latency", value=f"{round(total)}ms")
                embed.add_field(name="Servers", value=str(servers))

                await msg.edit(embed=embed)

            elif module == "exec":
                code = ctx.message.content.replace("d!admin exec ```py\n", "").replace("```", "")
                exec(code)
        else:
            await ctx.send(embed=discord.Embed(
                description="Only the developer behind this bot can use this command."
                            " If you are a server admin or moderator, make sure you have the manage messages"
                            " permission and use `d!config` instead. <:sg_clown:905847725948567554>."))


class moderation(commands.Cog):

    def __init__(self, bot):
        self.guild = None
        self.bot = bot

    @commands.command(description="Deletes previously sent messages.")
    @commands.bot_has_permissions(manage_messages=True)
    @has_permissions(manage_messages=True)
    async def purge(self, ctx, amount: int):
        if amount > 100:
            amount = 100
        await ctx.channel.purge(
            limit=amount + 1)

    @commands.command(description="Bans a specified user.")
    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, reason=None):
        if reason is not None:
            await member.ban(reason=reason)
            await ctx.send(f"User {member.mention} has been banned from {ctx.guild.name} for {reason}.")
        else:
            await member.ban()
            await ctx.send(f"User {member.mention} has been banned from {ctx.guild.name}.")

    @commands.command(description="Help Command")
    async def help(self, ctx, module):
        global botdata
        if ctx.author.id == bot.owner_id:
            if module == "admin":
                ctx.send("`.stats` \n"
                         "`.exec <py code block>` \n")
        else:
            await ctx.send(embed=discord.Embed(
                title="Help Command", color=discord.Colour.dark_blue(),
                thumbnail="https://www.creativefabrica.com/wp-content/uploads/2020/02/11/Fish-Logo-Graphics-1-16.jpg",
                add_field="`.ban` \n `.purge`"))


if __name__ == "__main__":
    botdata = DataIO(bot).createconfig("other")
    DataIO(bot).savetofile(botdata)
    bot.add_cog(restricted(bot))

    threading.Thread(target=syncdata, args=(bot,)).start()

    bot.run("TOKEN")
