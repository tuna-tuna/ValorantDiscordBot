import asyncio
from typing import Union
from typing import Optional

import requests
import aiohttp
from.sheet import Sheet
from decimal import Decimal, ROUND_HALF_UP

sheet = Sheet()

class Fetch:
    def __init__(self) -> None:
        self.headers = {'Content-type': 'application/json', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.62 Safari/537.36'}
        self.session = aiohttp.ClientSession()

    def registerId(self, author_id: str, valo_id: str, valo_tag: str) -> Optional[bool]:
        Url = 'https://api.henrikdev.xyz/valorant/v1/account/' + valo_id + '/' + valo_tag
        r = requests.get(Url, headers=self.headers)
        data = r.json()
        print(data)
        if data["status"] != 200:
            return False
        puuid = data["data"]["puuid"]
        newSheet = sheet.getSheet(author_id)
        newSheet.update_acell('A1',valo_id)
        newSheet.update_acell('B1',valo_tag)
        newSheet.update_acell('C1',puuid)
        return None

    async def fetchMatchHistory(self, id: str, tag: str, puuid: str, mode: str) -> dict:
        baseUrl = 'https://api.henrikdev.xyz/valorant/v3/by-puuid/matches/ap/' + puuid
        Url = baseUrl
        if mode == 'competitive':
            Url = baseUrl + '?filter=competitive'
        if mode == 'unrated':
            Url = baseUrl + '?filter=unrated'
        async with self.session.get(Url, headers = self.headers) as r:
            data = await r.json()
        if data["status"] == 408:
            async with self.session.get(Url, headers = self.headers) as r:
                data = await r.json()
        return data

    async def fetchMMRHistoryFixed(self, id: str, tag: str, puuid: str):
        Url = 'https://api.henrikdev.xyz/valorant/v1/by-puuid/mmr-history/ap/' + puuid
        async with self.session.get(Url, headers=self.headers) as r:
            data = await r.json()
        if data["status"] != 200:
            return False
        elolist = []
        rankcatlist = []
        rankpointlist = []
        i=0
        for matches in data["data"]:
            elo = matches["elo"]
            elolist.append(elo)
            rankcat = ""
            rankcatnum = (matches["currenttier"] % 3) + 1
            if matches["currenttier"] >= 3 and matches["currenttier"] <= 5:
                rankcat = "Iron"
            elif matches["currenttier"] >= 6 and matches["currenttier"] <= 8:
                rankcat = "Bronze"
            elif matches["currenttier"] >= 9 and matches["currenttier"] <= 11:
                rankcat = "Silver"
            elif matches["currenttier"] >= 12 and matches["currenttier"] <= 14:
                rankcat = "Gold"
            elif matches["currenttier"] >= 15 and matches["currenttier"] <= 17:
                rankcat = "Platinum"
            elif matches["currenttier"] >= 18 and matches["currenttier"] <= 20:
                rankcat = "Diamond"
            elif matches["currenttier"] >= 3 and matches["currenttier"] <= 5:
                rankcat = "Immortal"
            else:
                rankcat = "Radiant"
            rankcatlist.append(rankcat + ' ' + str(rankcatnum))
            rankpointlist.append(matches["ranking_in_tier"])
            i = i + 1
            if i == 5:
                break
        elomax = (50 - (max(elolist) % 50)) + max(elolist)
        elomin = min(elolist) - (min(elolist) % 50)
        elolen = len(elolist)
        eloplotlist = []
        for i in range(int(elomin/10), int((elomax/10) + 1)):
            eloplotlist.append(i*10)
        #Fetch Match Data
        matchdata = []
        data = await self.fetchMatchHistory(id, tag, puuid, 'competitive')
        i = 0
        for matches in data["data"]:
            metadata = matches["metadata"]
            map = metadata["map"]
            team = ""
            winlose = "Lose"
            score = ""
            for players in matches["players"]["all_players"]:
                if (players["name"]).lower() == id.lower() and (players["tag"]).lower() == tag.lower():
                    team = players["team"]
            score = str(matches["teams"][team.lower()]["rounds_won"]) + " - " + str(matches["teams"][team.lower()]["rounds_lost"])
            if matches["teams"][team.lower()]["rounds_won"] > matches["teams"][team.lower()]["rounds_lost"]:
                winlose = "Win"
            if matches["teams"][team.lower()]["rounds_won"] == matches["teams"][team.lower()]["rounds_lost"]:
                winlose = "Draw"
            matchstr = map + " " + winlose + "                          " + "\n" + score + "                          "
            matchdata.append(matchstr)
            i = i + 1
            if i == elolen:
                break
        matchdata.reverse()
        rankcatlist.reverse()
        rankpointlist.reverse()
        return elolist, elomax, elomin, eloplotlist, matchdata, rankcatlist, rankpointlist

    async def fetchMMRHistory(self, id: str, tag: str, puuid: str):
        postdata = {
            "type": "competitiveupdates",
            "value": puuid,
            "region": "ap",
            "queries": "?queue=competitive"
        }
        data = {}
        Url = 'https://api.henrikdev.xyz/valorant/v1/raw'
        async with self.session.post(url=Url, data=postdata, headers=self.headers) as r:
            data = await r.json()
        elolist = []
        rankcatlist = []
        rankpointlist = []
        i=0
        for matches in data["Matches"]:
            if matches["MapID"] == "":
                continue
            elo = (int(matches["TierAfterUpdate"]) - 3) * 100 + int(matches["RankedRatingAfterUpdate"])
            elolist.append(elo)
            rankcat = ""
            rankcatnum = str((int(matches["TierAfterUpdate"]) % 3) + 1)
            if int(matches["TierAfterUpdate"]) >= 3 and int(matches["TierAfterUpdate"]) <= 5:
                rankcat = "Iron"
            elif int(matches["TierAfterUpdate"]) >= 6 and int(matches["TierAfterUpdate"]) <= 8:
                rankcat = "Bronze"
            elif int(matches["TierAfterUpdate"]) >= 9 and int(matches["TierAfterUpdate"]) <= 11:
                rankcat = "Silver"
            elif int(matches["TierAfterUpdate"]) >= 12 and int(matches["TierAfterUpdate"]) <= 14:
                rankcat = "Gold"
            elif int(matches["TierAfterUpdate"]) >= 15 and int(matches["TierAfterUpdate"]) <= 17:
                rankcat = "Platinum"
            elif int(matches["TierAfterUpdate"]) >= 18 and int(matches["TierAfterUpdate"]) <= 20:
                rankcat = "Diamond"
            elif int(matches["TierAfterUpdate"]) >= 3 and int(matches["TierAfterUpdate"]) <= 5:
                rankcat = "Immortal"
            else:
                rankcat = "Radiant"
            rankcatlist.append(rankcat + ' ' + rankcatnum)
            rankpointlist.append(matches["RankedRatingAfterUpdate"])
            i = i + 1
            if i == 5:
                break
        elomax = (50 - (max(elolist) % 50)) + max(elolist)
        elomin = min(elolist) - (min(elolist) % 50)
        elolen = len(elolist)
        eloplotlist = []
        for i in range(int(elomin/10), int((elomax/10) + 1)):
            eloplotlist.append(i*10)
        #Fetch matches info
        matchdata = []
        data = await self.fetchMatchHistory(id, tag, puuid, 'competitive')
        i = 0
        for matches in data["data"]:
            metadata = matches["metadata"]
            map = metadata["map"]
            team = ""
            winlose = "Lose"
            score = ""
            for players in matches["players"]["all_players"]:
                if (players["name"]).lower() == id.lower() and (players["tag"]).lower() == tag.lower():
                    team = players["team"]
            score = str(matches["teams"][team.lower()]["rounds_won"]) + " - " + str(matches["teams"][team.lower()]["rounds_lost"])
            if matches["teams"][team.lower()]["rounds_won"] > matches["teams"][team.lower()]["rounds_lost"]:
                winlose = "Win"
            if matches["teams"][team.lower()]["rounds_won"] == matches["teams"][team.lower()]["rounds_lost"]:
                winlose = "Draw"
            matchstr = map + " " + winlose + "                          " + "\n" + score + "                          "
            matchdata.append(matchstr)
            i = i + 1
            if i == elolen:
                break
        matchdata.reverse()
        rankcatlist.reverse()
        rankpointlist.reverse()
        return elolist, elomax, elomin, eloplotlist, matchdata, rankcatlist, rankpointlist


    async def fetchCurrentRank(self, id: str, tag: str, puuid: str):
        Url = 'https://api.henrikdev.xyz/valorant/v1/by-puuid/mmr/ap/' + puuid
        async with self.session.get(Url, headers=self.headers) as r:
            data = await r.json()
        if data["status"] != 200:
            return False
        Url = 'https://valorant-api.com/v1/competitivetiers'
        async with self.session.get(Url, headers=self.headers) as r:
            data2 = await r.json()
        if data2["status"] != 200:
            return False
        currenttier = data["data"]["currenttier"]
        currentrank = data["data"]["currenttierpatched"]
        currentpoint = data["data"]["ranking_in_tier"]
        rankstr = currentrank + '\n' + str(currentpoint) + ' Points'
        if currentpoint == 1:
            rankstr = currentrank + '\n' + str(currentpoint) + ' Point'
        currentrank = currentrank.upper()
        currentrankimage = ""
        for episodes in data2["data"]:
            for tiers in episodes["tiers"]:
                if tiers["tierName"] == currentrank:
                    currentrankimage = tiers["largeIcon"]
                    break
            break
        if currenttier < 3:
            color = 0x2d302e
        elif currenttier < 6:
            color = 0x636363
        elif currenttier < 9:
            color = 0x8c7345
        elif currenttier < 12:
            color = 0x9c9c9c
        elif currenttier < 15:
            color = 0xbfc900
        elif currenttier < 18:
            color = 0x07abab
        elif currenttier < 21:
            color = 0x9f22e3
        elif currenttier < 24:
            color = 0xc40000
        else:
            color = 0xfcff47
        return rankstr, currentrankimage, color

    async def fetchPlayerIcon(self, id: str, tag: str) -> Union[bool, str]:
        Url = 'https://api.henrikdev.xyz/valorant/v1/account/' + id + '/' + tag
        async with self.session.get(Url, headers=self.headers) as r:
            data = await r.json()
        if data["status"] != 200:
            return False
        iconUrl = data["data"]["card"]["small"]
        return iconUrl

    async def fetchMatchData(self, id: str, tag: str, puuid: str, matchId: str) -> Union[bool, dict]:
        infoList = {}
        Url = 'https://api.henrikdev.xyz/valorant/v2/match/' + matchId
        async with self.session.get(Url, headers=self.headers) as r:
            data = await r.json()
        if data["status"] != 200:
            return False
        Map = data["data"]["metadata"]["map"]
        GameLength = Decimal(str(data["data"]["metadata"]["game_length"] / 60000)).quantize(Decimal(0), rounding=ROUND_HALF_UP)
        team = ""
        chara = ""
        kills = None
        deaths = None
        assists = None
        bodyshots = None
        headshots = None
        legshots = None
        acs = None
        winlose = ""
        score = ""
        for player in data["data"]["players"]["all_players"]:
            if player["puuid"] == puuid:
                team = player["team"]
                chara = player["character"]
                kills = player["stats"]["kills"]
                deaths = player["stats"]["deaths"]
                assists = player["stats"]["assists"]
                bodyshots = player["stats"]["bodyshots"]
                headshots = player["stats"]["headshots"]
                legshots = player["stats"]["legshots"]
                acs = Decimal(str(player["stats"]["score"] / data["data"]["metadata"]["rounds_played"])).quantize(Decimal(0), rounding=ROUND_HALF_UP)
        if data["data"]["teams"][team.lower()]["has_won"] == True:
            winlose = "Win"
        else:
            winlose = "Lose"
        if data["data"]["teams"][team.lower()]["rounds_won"] == data["data"]["teams"][team.lower()]["rounds_lost"]:
            winlose = "Draw"
        score = winlose + '  ' + str(data["data"]["teams"][team.lower()]["rounds_won"]) + ' - ' + str(data["data"]["teams"][team.lower()]["rounds_lost"])
        infoList["map"] = Map
        infoList["gamelength"] = GameLength
        infoList["team"] = team
        infoList["chara"] = chara
        infoList["kills"] = kills
        infoList["deaths"] = deaths
        infoList["assists"] = assists
        infoList["bodyshots"] = bodyshots
        infoList["headshots"] = headshots
        infoList["legshots"] = legshots
        infoList["acs"] = acs
        infoList["winlose"] = winlose
        infoList["score"] = score
        return infoList

    async def fetchMatchDataFixed(self, id: str, tag: str, puuid: str, mode: str) -> Union[bool, dict]:
        infoList = {}
        data = await self.fetchMatchHistory(id, tag, puuid, mode)
        if data["status"] != 200:
            return False
        for match in data["data"]:
            map = match["metadata"]["map"]
            GameLength = Decimal(str(match["metadata"]["game_length"] / 60000)).quantize(Decimal(0), rounding=ROUND_HALF_UP)
            rounds = match["metadata"]["rounds_played"]
            team = ""
            chara = ""
            kills = None
            deaths = None
            assists = None
            bodyshots = None
            headshots = None
            legshots = None
            acs = None
            winlose = ""
            for player in match["players"]["all_players"]:
                if player["puuid"] == puuid:
                    team = player["team"]
                    chara = player["character"]
                    kills = player["stats"]["kills"]
                    deaths = player["stats"]["deaths"]
                    assists = player["stats"]["assists"]
                    bodyshots = player["stats"]["bodyshots"]
                    headshots = player["stats"]["headshots"]
                    legshots = player["stats"]["legshots"]
                    acs = Decimal(str(player["stats"]["score"] / rounds)).quantize(Decimal(0), rounding=ROUND_HALF_UP)
            if match["teams"][team.lower()]["has_won"] == True:
                winlose = "Win"
            else:
                winlose = "Lose"
            if match["teams"][team.lower()]["rounds_won"] == match["teams"][team.lower()]["rounds_lost"]:
                winlose = "Draw"
            score = winlose + '  ' + str(match["teams"][team.lower()]["rounds_won"]) + ' - ' + str(match["teams"][team.lower()]["rounds_lost"])
            break
        infoList["map"] = map
        infoList["gamelength"] = GameLength
        infoList["team"] = team
        infoList["chara"] = chara
        infoList["kills"] = kills
        infoList["deaths"] = deaths
        infoList["assists"] = assists
        infoList["bodyshots"] = bodyshots
        infoList["headshots"] = headshots
        infoList["legshots"] = legshots
        infoList["acs"] = acs
        infoList["winlose"] = winlose
        infoList["score"] = score
        return infoList

    async def searchMatchForPlayer(self, id: str, tag: str, puuid: str, author_id: str) -> dict:
        eachPlayerList = {}
        eachPlayerList["id"] = id
        eachPlayerList["tag"] = tag
        eachPlayerList["author_id"] = author_id
        #Competitive
        cmpdata = await self.fetchMatchHistory(id, tag, puuid, 'competitive')
        try:
            for cmpmatches in cmpdata["data"]:
                compTime = cmpmatches["metadata"]["game_start"]
                compMatchId = cmpmatches["metadata"]["matchid"]
                break
        except:
            print(cmpdata)
        #Unrated
        unrdata = await self.fetchMatchHistory(id, tag, puuid, 'unrated')
        try:
            for unrmatches in unrdata["data"]:
                unrTime = unrmatches["metadata"]["game_start"]
                unrMatchId = unrmatches["metadata"]["matchid"]
                break
        except:
            print(unrdata)        
        if compTime > unrTime:
            whichMode = "Competitive"
            matchId = compMatchId
        else:
            whichMode = "Unrated"
            matchId = unrMatchId
        eachPlayerList["matchid"] = matchId
        eachPlayerList["mode"] = whichMode
        infoList = await self.fetchMatchDataFixed(id, tag, puuid, whichMode.lower())
        infoList.update(eachPlayerList)
        return infoList

    async def searchMatch(self, sheet: Sheet) -> list:
        worksheet_list = sheet.workbook.worksheets()
        data = None
        compTime = None
        unrTime = None
        compMatchId = None
        unrMatchId = None
        matchId = None
        whichMode = ""
        matchUpdateList = []
        eachPlayerList = {}
        successFlag = True
        for current in worksheet_list:
            if current.acell('A2').value == "off":
                continue
            elif current.acell('A2').value == "on":
                id, tag, puuid = sheet.checkStats(current.title)
                lastMatchId = current.acell('B2').value
                eachPlayerList["author_id"] = current.title
                eachPlayerList["id"] = id
                eachPlayerList["tag"] = tag
                eachPlayerList["puuid"] = puuid
                eachPlayerList["channel_id"] = current.acell('A3').value
                
                #Competitive
                await asyncio.sleep(5)
                data = await self.fetchMatchHistory(id, tag, puuid, "competitive")
                if data["status"] != 200:
                    await asyncio.sleep(3)
                    data = await self.fetchMatchHistory(id, tag, puuid, "competitive")
                try:
                    for matches in data["data"]:
                        compTime = matches["metadata"]["game_start"]
                        compMatchId = matches["metadata"]["matchid"]
                        break
                except:
                    print(data)
                    successFlag = False
                #Unrated
                await asyncio.sleep(5)
                data = await self.fetchMatchHistory(id, tag, puuid, 'unrated')
                if data["status"] != 200:
                    await asyncio.sleep(3)
                    data = await self.fetchMatchHistory(id, tag, puuid, 'unrated')
                try:
                    for matches in data["data"]:
                        unrTime = matches["metadata"]["game_start"]
                        unrMatchId = matches["metadata"]["matchid"]
                        break
                except:
                    print(data)
                    successFlag = False
                if successFlag == True:
                    if compTime > unrTime:
                        whichMode = "Competitive"
                        matchId = compMatchId
                    else:
                        whichMode = "Unrated"
                        matchId = unrMatchId
                    eachPlayerList["matchid"] = matchId
                    if lastMatchId != matchId:
                        eachPlayerList["update"] = "True"
                        current.update_acell('B2',matchId)
                    else:
                        eachPlayerList["update"] = "False"
                    eachPlayerList["mode"] = whichMode
                    infoList = await self.fetchMatchData(id, tag, puuid, matchId)
                    infoList.update(eachPlayerList)
                    matchUpdateList.append(infoList)
        return matchUpdateList
        
    async def fetchMapImage(self, name: str) -> Union[bool, str]:
        Url = 'https://valorant-api.com/v1/maps'
        async with self.session.get(Url, headers=self.headers) as r:
            data = await r.json()
        if data["status"] != 200:
            return False
        for maps in data["data"]:
            if name == maps["displayName"]:
                return maps["splash"]

    async def fetchPlayersStats(self, id: str, tag: str, puuid: str, mode: str) -> Union[bool, dict]:
        infoList = {}
        playersStats = {}
        playersStatsList = []
        data = await self.fetchMatchHistory(id, tag, puuid, mode)
        blueScore = 0
        redScore = 0
        if data["status"] != 200:
            return False
        for match in data["data"]:
            map = match["metadata"]["map"]
            GameLength = int(Decimal(str(match["metadata"]["game_length"] / 60000)).quantize(Decimal(0), rounding=ROUND_HALF_UP))
            rounds = match["metadata"]["rounds_played"]
            #team score
            blueScore = match["teams"]["blue"]["rounds_won"]
            redScore = match["teams"]["red"]["rounds_won"]
            #for each players
            name = ""
            tag = ""
            team = ""
            eachpuuid = ""
            chara = ""
            kills = None
            deaths = None
            assists = None
            bodyshots = None
            headshots = None
            legshots = None
            acs = None
            moneyspent = None
            damagemade = None
            econ = None
            #for the player
            score = ""
            winlose = ""
            for player in match["players"]["all_players"]:
                name = player["name"]
                tag = player["tag"]
                eachpuuid = player["puuid"]
                team = player["team"]
                chara = player["character"]
                kills = player["stats"]["kills"]
                deaths = player["stats"]["deaths"]
                assists = player["stats"]["assists"]
                bodyshots = player["stats"]["bodyshots"]
                headshots = player["stats"]["headshots"]
                legshots = player["stats"]["legshots"]
                rank = player["currenttier"]
                if bodyshots == None:
                    bodyshots = 0
                if headshots == None:
                    headshots = 0
                if legshots == None:
                    legshots = 0
                acs = int(Decimal(str(player["stats"]["score"] / rounds)).quantize(Decimal(0), rounding=ROUND_HALF_UP))
                moneyspent = player["economy"]["spent"]["overall"]
                damagemade = player["damage_made"]
                if player["puuid"] == puuid:
                    if match["teams"][team.lower()]["has_won"] == True:
                        winlose = "Win"
                    else:
                        winlose = "Lose"
                    if match["teams"][team.lower()]["rounds_won"] == match["teams"][team.lower()]["rounds_lost"]:
                        winlose = "Draw"
                    score = winlose + '  ' + str(match["teams"][team.lower()]["rounds_won"]) + ' - ' + str(match["teams"][team.lower()]["rounds_lost"])
                    playersStats["winlose"] = winlose
                    playersStats["score"] = score
                roundCount = 0
                firstbloods = 0
                for roundStats in match["kills"]:
                    if roundStats["round"] == roundCount:
                        roundCount += 1
                        if roundStats["killer_puuid"] == eachpuuid:
                            firstbloods += 1
                playersStats["name"] = name
                playersStats["tag"] = tag
                playersStats["team"] = team
                playersStats["chara"] = chara
                playersStats["kills"] = kills
                playersStats["deaths"] = deaths
                playersStats["assists"] = assists
                playersStats["bodyshots"] = bodyshots
                playersStats["headshots"] = headshots
                playersStats["legshots"] = legshots
                playersStats["rank"] = rank
                playersStats["acs"] = acs
                playersStats["econ"] = round(damagemade / moneyspent * 1000)
                playersStats["fbs"] = firstbloods
                playersStatsList.append(playersStats.copy())
            break
        infoList["map"] = map
        infoList["gamelength"] = GameLength
        infoList["blueScore"] = blueScore
        infoList["redScore"] = redScore
        playersStatsList.sort(key=lambda x: x["acs"], reverse=True)
        infoList["players"] = playersStatsList
        return infoList

    async def updateRiotId(self, sheet: Sheet, channel) -> None:
        print('Checking riot id...')
        puuidList = []
        authorIdList = []
        updateList = []
        worksheet_list = sheet.workbook.worksheets()
        for current in worksheet_list:
            try:
                puuid = current.acell('C1').value
                puuidList.append(puuid)
                authorIdPuuid = {
                    "authorId": current.title,
                    "puuid": puuid
                }
                authorIdList.append(authorIdPuuid.copy())
            except Exception as e:
                print(e)
        async with self.session.put('https://pd.ap.a.pvp.net/name-service/v2/players', json=puuidList) as r:
            data = await r.json(content_type=None)
        for playerData in data:
            puuid = playerData["Subject"]
            authorId = ''
            for eachData in authorIdList:
                if eachData["puuid"] == puuid:
                    authorId = eachData["authorId"]
            playerIds = {
                "authorId": authorId,
                "id": playerData["GameName"],
                "tag": playerData["TagLine"]
            }
            updateList.append(playerIds.copy())
        for playerId in updateList:
            currentSheet = sheet.getSheet(playerId["authorId"])
            currentSheet.update_acell('A1', playerId["id"])
            currentSheet.update_acell('B1', playerId["tag"])
        await channel.send(str(updateList))
        print('Successfully updated Riot IDs')
        return