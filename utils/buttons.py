import discord
from datetime import datetime, timezone, timedelta

from .fetch import Fetch
from .db import DataBase
from.local import Local

fetch = Fetch()
db = DataBase()
local = Local()
from PIL import Image

class MatchButton(discord.ui.Button):
    def __init__(self, label: str, matchId: str, author_id: str, winlose: str):
        super().__init__(
            label=label,
            style=discord.ButtonStyle.primary if winlose == 'Win' else discord.ButtonStyle.danger if winlose == 'Lose' else discord.ButtonStyle.secondary,
            custom_id=matchId
        )
        self.author_id = author_id

    async def callback(self, interaction: discord.Interaction):
        try:
            self.disabled = True
            await interaction.response.edit_message(view=self.view)
            msg = await interaction.followup.send(content='Fetching data...  This may take about 30secs.', wait=True)
            player = await fetch.fetchMatchRaw(matchid=self.custom_id)
            id, tag, puuid = db.checkStats(str(self.author_id))
            if id == False:
                await interaction.followup.edit_message(content='Please register your valorant id and tag before using this command.')
                return
            player = await fetch.fetchMatchRaw(self.custom_id)
            if type(player) != dict:
                await interaction.followup.edit_message(content='Error!')
                return
            scorestats = await fetch.fetchPlayersStatsByMatchId(self.custom_id, puuid)
            gamelength = scorestats["gamelength"]
            map = scorestats["map"]
            gamestartunix = player["data"]["metadata"]["game_start"]
            gamestartjst = datetime.fromtimestamp(gamestartunix, tz=timezone(timedelta(hours=9)))
            gamestart = gamestartjst.strftime('%m/%d %H:%M')
            team = ''
            titleStr = ''
            winlose = ''
            chara = ''
            kills = 0
            deaths = 0
            assists = 0
            bodyshots = 0
            headshots = 0
            legshots = 0
            acs = 0
            mode = player["data"]["metadata"]["mode"]
            for playerDataRaw in player["data"]["players"]["all_players"]:
                if playerDataRaw["puuid"] == puuid:
                    team = playerDataRaw["team"]
            if team == 'Blue':
                titleStr = str(scorestats["blueScore"]) + ' - ' + str(scorestats["redScore"]) + ' (' + str(gamelength) + 'mins)'
                if scorestats["blueScore"] > scorestats["redScore"]:
                    winlose = 'Win'
                elif scorestats["redScore"] > scorestats["blueScore"]:
                    winlose = 'Lose'
                else:
                    winlose = 'Draw'
            else:
                titleStr = str(scorestats["redScore"]) + ' - ' + str(scorestats["blueScore"]) + ' (' + str(gamelength) + 'mins)'
                if scorestats["blueScore"] < scorestats["redScore"]:
                    winlose = 'Win'
                elif scorestats["redScore"] < scorestats["blueScore"]:
                    winlose = 'Lose'
                else:
                    winlose = 'Draw'
            titleStr = winlose + '  ' + titleStr
            for playerData in scorestats["players"]:
                if playerData["name"] == id and playerData["tag"] == tag and playerData["team"] == team:
                    chara = playerData["chara"]
                    kills = playerData["kills"]
                    deaths = playerData["deaths"]
                    assists = playerData["assists"]
                    bodyshots = playerData["bodyshots"]
                    headshots = playerData["headshots"]
                    legshots = playerData["legshots"]
                    acs = playerData["acs"]
            mappath = './assets/maps/' + map + '.png'
            mapImage = Image.open(mappath).copy()
            scoreboardpath = local.makeScoreImage(id,tag, scorestats, str(self.author_id))
            scoreboardImage = Image.open(scoreboardpath).copy()
            mapImage.paste(scoreboardImage,(310,140))
            mapImage.save('./tmp/' + str(self.author_id) + '_scoremap.png')
            matchid = player["data"]["metadata"]["matchid"]
            if winlose == "Win":
                color = 0x03fc7f
            elif winlose == "Lose":
                color = 0xd10217
            else:
                color = 0xb0ffd7
            embed = discord.Embed(color=color)
            iconUrl = await fetch.fetchPlayerIcon(id,tag)
            embed.set_author(name = id + '#' + tag + '\'s match detail', icon_url=iconUrl)
            embed.add_field(name = '```' + titleStr + '```', value='Map: ' + map + '\nCharacter: ' + chara + '\nKDA: ' + str(kills) + '/' + str(deaths) + '/' + str(assists) + '\nAverageCombatScore: ' + str(acs) + '\nMode: ' + mode + '\nGameStart: ' + gamestart + '\n[Click here to view more detail on tracker.]({})'.format('https://tracker.gg/valorant/match/' + matchid))
            local.makeShotsImage(bodyshots, headshots, legshots, str(self.author_id))
            thumbnail = discord.File('./tmp/' + str(self.author_id) + '.png')
            image = discord.File('./tmp/' + str(self.author_id) + '_scoremap.png')
            embed.set_thumbnail(url='attachment://' + str(self.author_id) + '.png')
            embed.set_image(url='attachment://' + str(self.author_id) + '_scoremap.png')
            await msg.edit(content=None, embed=embed, files=[thumbnail, image])
            return
        except Exception as e:
            raise e
