import time
import discord
from discord.ext import commands
from discord.ext.commands import has_permissions

intents = discord.Intents().all()
Client = commands.Bot(command_prefix="$", intents=intents)
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='.', intents=intents, help_command=None)
bot.owner_id = 933369720361586699
status = "for Rule Breakers"


@bot.event
async def on_ready():
    global botdata

    print("Bot online")
    # this line automatically makes the bot go into "playing a game" mode.
    activity = discord.Activity(type=discord.ActivityType.watching, name=f"{status}")
    await bot.change_presence(status=discord.Status.idle, activity=activity)


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
                ctx.send(embed=discord.Embed(title="Admin Commands", color=discord.Colour.dark_blue(),
                                             add_field="`.stats` \n `.exec <py code block>` \n"))
        else:
            await ctx.send(embed=discord.Embed(
                title="Help Command", color=discord.Colour.dark_blue(),
                thumbnail="https://www.creativefabrica.com/wp-content/uploads/2020/02/11/Fish-Logo-Graphics-1-16.jpg",
                add_field="`.ban` \n `.purge`"))


if __name__ == "__main__":

    bot.run("OTUyNzA4OTc2Njg3MDgzNTMw.Yi59YA.xdanwPtQcGy5AfAU7BI_jo3t_As")
