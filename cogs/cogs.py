from discord.commands import slash_command, Option
from discord.ext import commands
import sys
import requests
import os

sys.path.append('../')

from utils.fetch import Fetch
from utils.local import Local
from utils.db import DataBase

import discord
import matplotlib.pyplot as plt
from PIL import Image

fetch = Fetch()
local = Local()
db = DataBase()

guild_ids = [499227608807112724]

class Register(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @slash_command()
    async def register(self, ctx: discord.ApplicationContext, id: str, tag: str):
        """Riotアカウントを登録することができます"""
        try:
            await ctx.defer(ephemeral = True)
            commandName = sys._getframe().f_code.co_name
            await local.onCommand(self.bot, ctx, commandName)
            exist = fetch.registerId(str(ctx.author.id), str(id), str(tag))
            if exist == False:
                await ctx.respond('Error! Please try again later.')
                return
            await ctx.respond('Your Riot ID: '+ id +' #'+ tag +' registered.')
            return
        except Exception as e:
            await local.onError(self.bot, sys._getframe().f_code.co_name, e)
            await ctx.respond('Error occured')

class Stats(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @slash_command()
    async def stats(self, ctx: discord.ApplicationContext):
        """各種スタッツのtrackerへのリンクを表示します"""
        try:
            commandName = sys._getframe().f_code.co_name
            await local.onCommand(self.bot, ctx, commandName)
            id, tag, puuid = db.checkStats(str(ctx.author.id))
            if id == False:
                await ctx.respond('Please register your valorant id and tag before using this command.')
                return
            titleStr = id + '#' + tag + '\'s stats'
            baseUrl = 'https://tracker.gg/valorant/profile/riot/' + id + '%23' + tag
            overviewUrl = baseUrl + '/overview'
            unratedUrl = baseUrl + '/matches'
            competitiveUrl = baseUrl + '/matches?playlist=competitive'
            agentUrl = baseUrl + '/agents'
            weaponsUrl = baseUrl + '/weapons'
            embed = discord.Embed(title=titleStr, description = 'Click these links to open tracker sites.')
            embed.add_field(name="Overview Stats",value="[Click here to open.]({})".format(overviewUrl),inline=False)
            embed.add_field(name="Unrated Stats",value="[Click here to open.]({})".format(unratedUrl),inline=False)
            embed.add_field(name="Competitive Stats",value="[Click here to open.]({})".format(competitiveUrl),inline=True)
            embed.add_field(name="Agents Stats",value="[Click here to open.]({})".format(agentUrl),inline=False)
            embed.add_field(name="Weapons Stats",value="[Click here to open.]({})".format(weaponsUrl),inline=True)
            await ctx.respond(embed=embed)
        except Exception as e:
            await local.onError(self.bot, sys._getframe().f_code.co_name, e)
            await ctx.respond('Error occured')

class RankPoint(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command()
    async def rankpoint(self, ctx: discord.ApplicationContext):
        """現在のランクと過去数試合分のランクポイントの変動を見ることができます"""
        try:
            await ctx.defer()
            commandName = sys._getframe().f_code.co_name
            await local.onCommand(self.bot, ctx, commandName)
            message = await ctx.respond("Fetching data...")
            id, tag, puuid = db.checkStats(str(ctx.author.id))
            if id == False:
                await message.edit(content='Please register your valorant id and tag before using this command.')
                return
            titleStr = id + '#' + tag + '\'s RP history'
            embed = discord.Embed(title=titleStr)
            try:
                elolist, elomax, elomin, eloplotlist, matchdata, rankcatlist, rankpointlist = await fetch.fetchMMRHistory(id, tag, puuid)
            except:
                elolist, elomax, elomin, eloplotlist, matchdata, rankcatlist, rankpointlist = await fetch.fetchMMRHistoryFixed(id, tag, puuid)
            elolist.reverse()
            elolen = len(elolist)
            x = []
            y = []
            for i in range(1,elolen + 1):
                x.append(i)
            if elomax - elomin >= 100:
                for i in range(elomin, elomax + 1):
                    if i % 20 == 0:
                        y.append(i)
            else:
                for i in range(elomin, elomax + 1):
                    if i % 10 == 0:
                        y.append(i)
            yticklist = local.convertElo(y)
            fig, ax = plt.subplots()
            ax.plot(x,elolist,"o-")
            ax.set_title('MMR History')
            ax.set_ylabel('Rank Point')
            ax.set_ylim(elomin,elomax)
            ax.set_xticks(x)
            matchdata[0] = ''
            ax.set_xticklabels(matchdata)
            ax.set_yticks(y)
            ax.set_yticklabels(yticklist)
            ax.grid()
            for i in range(0,elolen):
                text = str(rankcatlist[i]) + '\n' + str(rankpointlist[i])
                ax.text(i + 1, elolist[i] + ((elomax - elomin) / 20), text, horizontalalignment="center", verticalalignment="center")
            fig.savefig("./tmp/test.png")
            iconUrl = await fetch.fetchPlayerIcon(id, tag)
            rankstr, currentrankimage, color = await fetch.fetchCurrentRank(id, tag, puuid)
            file = discord.File("./tmp/test.png", filename="test.png")
            titleStr = id + '#' + tag + '\'s Rank Point History'
            embed = discord.Embed(color=color)
            embed.set_author(name = titleStr, icon_url=iconUrl)
            embed.set_image(url="attachment://test.png")
            embed.add_field(name="Current Rank",value=rankstr)
            embed.set_thumbnail(url=currentrankimage)
            msg = await ctx.fetch_message(message.id)
            await msg.edit(content=None, embed=embed, file=file)
        except Exception as e:
            await local.onError(self.bot, sys._getframe().f_code.co_name, e)
            await ctx.respond('Error occured')

class MatchHistory(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command()
    async def competitivehistory(self, ctx: discord.ApplicationContext):
        """コンペティティブマッチの過去数試合分の結果を見ることができます"""
        try:
            await ctx.defer()
            commandName = sys._getframe().f_code.co_name
            await local.onCommand(self.bot, ctx, commandName)
            message = await ctx.respond("Fetching data...")
            id, tag, puuid = db.checkStats(str(ctx.author.id))
            if id == False:
                await message.edit(content='Please register your valorant id and tag before using this command.')
                return
            data = await fetch.fetchMatchHistory(id, tag, puuid, 'competitive')
            if data["status"] != 200:
                await ctx.send('Error')
                return
            titleStr = id + '#' + tag + '\'s Competitive Match History'
            embed = discord.Embed()
            matchNum = 0
            iconUrl = await fetch.fetchPlayerIcon(id, tag)
            for matches in data["data"]:
                metadata = matches["metadata"]
                map = metadata["map"]
                matchid = metadata["matchid"]
                team = ""
                chara = ""
                winlose = "Lose"
                score = ""
                matchesurl = 'https://tracker.gg/valorant/profile/riot/' + id + '%23' + tag + '/matches?playlist=competitive'
                for players in matches["players"]["all_players"]:
                    if (players["name"]).lower() == id.lower() and (players["tag"]).lower() == tag.lower():
                        team = players["team"]
                        chara = players["character"]
                score = str(matches["teams"][team.lower()]["rounds_won"]) + " - " + str(matches["teams"][team.lower()]["rounds_lost"])
                if matches["teams"][team.lower()]["rounds_won"] > matches["teams"][team.lower()]["rounds_lost"]:
                    winlose = "Win"
                if matches["teams"][team.lower()]["rounds_won"] == matches["teams"][team.lower()]["rounds_lost"]:
                    winlose = "Draw"
                if matchNum == 0:
                    embed.set_author(name = titleStr,icon_url=iconUrl)
                matchNum = matchNum + 1
                name = str(matchNum) + '.  ' + winlose + '(' + score + ')' + '  Map: ```' + map + '```  Character: ```' + chara + '```'
                detailUrl = 'https://tracker.gg/valorant/match/' + matchid + '?handle=' + id + '%23' + tag
                embed.add_field(name=name, value="[Click here to open detail.]({})".format(detailUrl),inline=False)
            embed.add_field(name='\u2800', value="[Click here to view more matches.]({})".format(matchesurl),inline=False)
            msg = await ctx.fetch_message(message.id)
            await msg.edit(content=None, embed=embed)
        except Exception as e:
            await local.onError(self.bot, sys._getframe().f_code.co_name, e)
            await ctx.respond('Error occured')

    @slash_command()
    async def unratedhistory(self, ctx: discord.ApplicationContext):
        """アンレートマッチの過去数試合分の結果を見ることができます"""
        try:
            await ctx.defer()
            commandName = sys._getframe().f_code.co_name
            await local.onCommand(self.bot, ctx, commandName)
            message = await ctx.respond("Fetching data...")
            id, tag, puuid = db.checkStats(str(ctx.author.id))
            if id == False:
                await message.edit(content='Please register your valorant id and tag before using this command.')
                return
            data = await fetch.fetchMatchHistory(id, tag, puuid, 'unrated')
            if data["status"] != 200:
                await ctx.respond('Error')
                return
            titleStr = id + '#' + tag + '\'s Unrated Match History'
            embed = discord.Embed()
            matchNum = 0
            iconUrl = await fetch.fetchPlayerIcon(id, tag)
            matchids = []
            for matches in data["data"]:
                metadata = matches["metadata"]
                map = metadata["map"]
                matchid = metadata["matchid"]
                matchids.append(matchid)
                team = ""
                chara = ""
                winlose = "Lose"
                score = ""
                matchesurl = 'https://tracker.gg/valorant/profile/riot/' + id + '%23' + tag + '/matches'
                for players in matches["players"]["all_players"]:
                    if (players["name"]).lower() == id.lower() and (players["tag"]).lower() == tag.lower():
                        team = players["team"]
                        chara = players["character"]
                score = str(matches["teams"][team.lower()]["rounds_won"]) + " - " + str(matches["teams"][team.lower()]["rounds_lost"])
                if matches["teams"][team.lower()]["rounds_won"] > matches["teams"][team.lower()]["rounds_lost"]:
                    winlose = "Win"
                if matches["teams"][team.lower()]["rounds_won"] == matches["teams"][team.lower()]["rounds_lost"]:
                    winlose = "Draw"
                if matchNum == 0:
                    embed.set_author(name = titleStr,icon_url=iconUrl)
                matchNum = matchNum + 1
                name = str(matchNum) + '.  ' + winlose + '(' + score + ')' + '  Map: ```' + map + '```  Character: ```' + chara + '```'
                detailUrl = 'https://tracker.gg/valorant/match/' + matchid + '?handle=' + id + '%23' + tag
                embed.add_field(name=name, value="[Click here to open detail.]({})".format(detailUrl),inline=False)
            embed.add_field(name='\u2800', value="[Click here to view more matches.]({})".format(matchesurl),inline=False)
            msg = await ctx.fetch_message(message.id)
            await msg.edit(content=None, embed=embed)
        except Exception as e:
            await local.onError(self.bot, sys._getframe().f_code.co_name, e)
            await ctx.respond('Error occured')

    @slash_command()
    async def lastmatch(self, ctx: discord.ApplicationContext):
        """直近のアンレートまたはコンペティティブマッチの結果を表示します"""
        try:
            await ctx.defer()
            commandName = sys._getframe().f_code.co_name
            await local.onCommand(self.bot, ctx, commandName)
            message = await ctx.respond("Fetching data...  This may take about 30secs.")
            id, tag, puuid = db.checkStats(str(ctx.author.id))
            if id == False:
                await message.edit(content='Please register your valorant id and tag before using this command.')
                return
            player = await fetch.searchMatchForPlayer(id, tag, puuid, str(ctx.author.id))
            if type(player) != dict:
                await ctx.respond('Error')
                return
            gamelength = player["gamelength"]
            titleStr =player["score"] + ' (' + str(gamelength) + 'mins)'
            map = player["map"]
            mappath = './assets/maps/' + map + '.png'
            mapImage = Image.open(mappath).copy()
            scorestats = await fetch.fetchPlayersStats(id, tag, puuid, player["mode"].lower())
            scoreboardpath = local.makeScoreImage(id,tag, scorestats, str(ctx.author.id))
            scoreboardImage = Image.open(scoreboardpath).copy()
            mapImage.paste(scoreboardImage,(310,140))
            mapImage.save('./tmp/' + str(ctx.author.id) + '_scoremap.png')
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
            embed.add_field(name = '```' + titleStr + '```', value='Map: ' + map + '\nCharacter: ' + chara + '\nKDA: ' + str(kills) + '/' + str(deaths) + '/' + str(assists) + '\nAverageCombatScore: ' + str(acs) + '\nMode: ' + mode + '\n[Click here to view more detail on tracker.]({})'.format('https://tracker.gg/valorant/match/' + matchid))
            local.makeShotsImage(bodyshots, headshots, legshots, player["author_id"])
            thumbnail = discord.File('./tmp/' + str(ctx.author.id) + '.png')
            image = discord.File('./tmp/' + str(ctx.author.id) + '_scoremap.png')
            embed.set_thumbnail(url='attachment://' + str(ctx.author.id) + '.png')
            embed.set_image(url='attachment://' + str(ctx.author.id) + '_scoremap.png')
            msg = await ctx.fetch_message(message.id)
            await msg.edit(content=None, embed=embed, files=[thumbnail, image])
            return
        except Exception as e:
            await local.onError(self.bot, sys._getframe().f_code.co_name, e)
            await ctx.respond('Error occured')

    @slash_command()
    async def vct(self, ctx: discord.ApplicationContext):
        try:
            await ctx.defer()
            commandName = sys._getframe().f_code.co_name
            await local.onCommand(self.bot, ctx, commandName)
            message = await ctx.respond("Fetching data...  This may take about 30secs.")
            id, tag, puuid = db.checkStats(str(ctx.author.id))
            if id == False:
                await ctx.respond('Please register your valorant id and tag before using this command.')
                return
            player = await fetch.searchMatchForPlayer(id, tag, puuid, str(ctx.author.id))
            scorestats = await fetch.fetchPlayersStats(id, tag, puuid, player["mode"].lower())
            vctpath = local.makeVCTImage(id,tag, scorestats, str(ctx.author.id))
            embed = discord.Embed()
            image = discord.File(vctpath)
            embed.set_image(url='attachment://' + str(ctx.author.id) + '_vct.png')
            msg = await ctx.fetch_message(message.id)
            await msg.edit(content=None, embed=embed, file=image)
        except Exception as e:
            await local.onError(self.bot, sys._getframe().f_code.co_name, e)
            await ctx.respond('Error occured')

class Others(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @slash_command()
    @discord.option(
        "toggle",
        description="on: Enable MatchTracking, off: Disable MatchTracking",
        autocomplete=discord.utils.basic_autocomplete(["on", "off"]),
    )
    async def trackmatch(self, ctx: discord.ApplicationContext, toggle: str):
        """このコマンドを実行したチャンネルに、プレイしたマッチの結果が送信されるようになります"""
        try:
            await ctx.defer(ephemeral=True)
            commandName = sys._getframe().f_code.co_name
            await local.onCommand(self.bot, ctx, commandName)
            id, tag, puuid = db.checkStats(str(ctx.author.id))
            if id == False:
                await ctx.respond('Please register your valorant id and tag before using this command.')
                return
            result = db.toggelTrack(str(ctx.author.id), toggle, ctx.channel.id)
            if result == True:
                await ctx.respond("Your match data will be tracked on this channel.")
            elif result == False:
                await ctx.respond("Your match data will no longer be tracked.")
        except Exception as e:
            await local.onError(self.bot, sys._getframe().f_code.co_name, e)
            await ctx.respond('Error occured')
    
def setup(bot: discord.Bot):
    bot.add_cog(Register(bot))
    bot.add_cog(Stats(bot))
    bot.add_cog(RankPoint(bot))
    bot.add_cog(MatchHistory(bot))
    bot.add_cog(Others(bot))