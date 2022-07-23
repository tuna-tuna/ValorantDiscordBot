import discord
from discord.ext import commands, tasks
from PIL import Image
from utils.fetch import Fetch
from utils.local import Local

local = Local()
fetch = Fetch()

class Tasks(commands.Cog):
    def __init__(self, bot: discord.Bot) -> None:
        self.bot = bot
        self.checkMatch.start()

    def cog_unload(self) -> None:
        self.checkMatch.cancel()

    async def checkMatchTask(self):
        try:
            matchUpdateList = await fetch.searchMatch()
            for player in matchUpdateList:
                if player["update"] == "True":
                    id = player["id"]
                    tag = player["tag"]
                    puuid = player["puuid"]
                    author_id = player["author_id"]
                    channel_id = player["channel_id"]
                    gamelength = player["gamelength"]
                    titleStr = '```' + player["score"] + ' (' + str(gamelength) + 'mins)' + '```'
                    map = player["map"]
                    mappath = './assets/maps/' + map + '.png'
                    mapImage = Image.open(mappath).copy()
                    scorestats = await fetch.fetchPlayersStats(id, tag, puuid, player["mode"].lower())
                    scoreboardpath = local.makeScoreImage(id,tag, scorestats, player["author_id"])
                    scoreboardImage = Image.open(scoreboardpath).copy()
                    mapImage.paste(scoreboardImage,(310,140))
                    mapImage.save('./tmp/' + player["author_id"] + '_scoremap.png')
                    chara = player["chara"]
                    kills = player["kills"]
                    deaths = player["deaths"]
                    assists = player["assists"]
                    bodyshots = player["bodyshots"]
                    headshots = player["headshots"]
                    legshots = player["legshots"]
                    acs = player["acs"]
                    mode = player["mode"]
                    matchid = player["matchid"]
                    if player["winlose"] == "Win":
                        color = 0x03fc7f
                    elif player["winlose"] == "Lose":
                        color = 0xd10217
                    else:
                        color = 0xb0ffd7
                    embed = discord.Embed(color=color)
                    iconUrl = await fetch.fetchPlayerIcon(id,tag)
                    embed.set_author(name = id + '#' + tag + '\'s last match detail', icon_url=iconUrl)
                    embed.add_field(name = titleStr, value='Map: ' + map + '\nCharacter: ' + chara + '\nKDA: ' + str(kills) + '/' + str(deaths) + '/' + str(assists) + '\nAverageCombatScore: ' + str(acs) + '\nMode: ' + mode + '\n[Click here to view more detail on tracker.]({})'.format('https://tracker.gg/valorant/match/' + matchid))
                    local.makeShotsImage(bodyshots, headshots, legshots, player["author_id"])
                    thumbnail = discord.File('./tmp/' + player["author_id"] + '.png')
                    image = discord.File('./tmp/' + player["author_id"] + '_scoremap.png')
                    embed.set_thumbnail(url='attachment://' + player["author_id"] + '.png')
                    embed.set_image(url='attachment://' + player["author_id"] + '_scoremap.png')
                    channel = self.bot.get_channel(int(channel_id))
                    if channel is None:
                        user: discord.User = await self.bot.fetch_user(int(author_id))
                        await user.send(files=[thumbnail, image], embed=embed)
                    else:
                        await channel.send(files=[thumbnail, image], embed=embed)

        except Exception as e:
            print('Exception occured while executing task.')
            print(e)

    @tasks.loop(seconds=300)
    async def checkMatch(self):
        await self.checkMatchTask()


    @checkMatch.before_loop
    async def beforecheckMatch(self):
        await self.bot.wait_until_ready()

def setup(bot: discord.Bot):
    bot.add_cog(Tasks(bot))