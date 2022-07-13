from PIL import Image, ImageFont, ImageDraw
from decimal import ROUND_HALF_UP, Decimal
from dotenv import load_dotenv
import os
import unicodedata
import discord

class Local:
    def __init__(self) -> None:
        load_dotenv()
        self.LOG_CHANNEL = int(os.environ['DISCORD_LOG_CHANNEL'])

    def convertElo(self, yticklist):
        ylist = []
        for i in yticklist:
            rankcatmin = ""
            rankpoint = str(i % 100)
            if yticklist.index(i) == 0 or yticklist.index(i) == 5:
                if i < 100:
                    rankcatmin = "Iron 1"
                    ylist.append(rankcatmin)
                    continue
                elif i < 200:
                    rankcatmin = "Iron 2"
                    ylist.append(rankcatmin)
                    continue
                elif i < 300:
                    rankcatmin = "Iron 3"
                    ylist.append(rankcatmin)
                    continue
                elif i < 400:
                    rankcatmin = "Bronze 1"
                    ylist.append(rankcatmin)
                    continue
                elif i < 500:
                    rankcatmin = "Bronze 2"
                    ylist.append(rankcatmin)
                    continue
                elif i < 600:
                    rankcatmin = "Bronze 3"
                    ylist.append(rankcatmin)
                    continue
                elif i < 700:
                    rankcatmin = "Silver 1"
                    ylist.append(rankcatmin)
                    continue
                elif i < 800:
                    rankcatmin = "Silver 2"
                    ylist.append(rankcatmin)
                    continue
                elif i < 900:
                    rankcatmin = "Silver 3"
                    ylist.append(rankcatmin)
                    continue
                elif i < 1000:
                    rankcatmin = "Gold 1"
                    ylist.append(rankcatmin)
                    continue
                elif i < 1100:
                    rankcatmin = "Gold 2"
                    ylist.append(rankcatmin)
                    continue
                elif i < 1200:
                    rankcatmin = "Gold 3"
                    ylist.append(rankcatmin)
                    continue
                elif i < 1300:
                    rankcatmin = "Platinum 1"
                    ylist.append(rankcatmin)
                    continue
                elif i < 1400:
                    rankcatmin = "Platinum 2"
                    ylist.append(rankcatmin)
                    continue
                elif i < 1500:
                    rankcatmin = "Platinum 3"
                    ylist.append(rankcatmin)
                    continue
                elif i < 1600:
                    rankcatmin = "Diamond 1"
                    ylist.append(rankcatmin)
                    continue
                elif i < 1700:
                    rankcatmin = "Diamond 2"
                    ylist.append(rankcatmin)
                    continue
                elif i < 1800:
                    rankcatmin = "Diamond 3"
                    ylist.append(rankcatmin)
                    continue
                elif i < 1900:
                    rankcatmin = "Ascendant 1"
                    ylist.append(rankcatmin)
                    continue
                elif i < 2000:
                    rankcatmin = "Ascendant 2"
                    ylist.append(rankcatmin)
                    continue
                elif i < 2100:
                    rankcatmin = "Ascendant 3"
                    ylist.append(rankcatmin)
                    continue
                elif i < 2200:
                    rankcatmin = "Immortal 1"
                    ylist.append(rankcatmin)
                    continue
                elif i < 2300:
                    rankcatmin = "Immortal 2"
                    ylist.append(rankcatmin)
                    continue
                elif i < 2400:
                    rankcatmin = "Immortal 3"
                    ylist.append(rankcatmin)
                    continue
                else:
                    rankcatmin = "Radiant"
                    ylist.append(rankcatmin)
                    continue
            ylist.append(rankpoint)
        return ylist

    def add_text_to_image(self, img, text, font_path, font_size, font_color, height, width, max_length=740):
        position = (width, height)
        font = ImageFont.truetype(font_path, font_size)
        draw = ImageDraw.Draw(img)
        if draw.textsize(text, font=font)[0] > max_length:
            while draw.textsize(text + '…', font=font)[0] > max_length:
                text = text[:-1]
            text = text + '…'
        draw.text(position, text, font_color, font=font)
        return img

    def makeShotsImage(self, bodyshots, headshots, legshots, author_id: str):
        if bodyshots == None:
            bodyshots = 0
        if headshots == None:
            headshots = 0
        if legshots == None:
            legshots = 0
        total = bodyshots + headshots + legshots
        bodyrate = Decimal(str(bodyshots / total * 100)).quantize(Decimal(0), rounding=ROUND_HALF_UP)
        headrate = Decimal(str(headshots / total * 100)).quantize(Decimal(0), rounding=ROUND_HALF_UP)
        legrate = Decimal(str(legshots / total * 100)).quantize(Decimal(0), rounding=ROUND_HALF_UP)
        picto = Image.open('./assets/shots.jpg').copy()
        font_path = './assets/NotoSansJP-Regular.otf'
        font_size = 100
        font_color = (127,127,127)
        height = 130
        width = 300
        img = self.add_text_to_image(picto, str(bodyrate) + '%', font_path, font_size, font_color, height, width)
        height = 5
        font_color = (0,0,0)
        img = self.add_text_to_image(picto, str(headrate) + '%', font_path, font_size, font_color, height, width)
        height = 300
        img = self.add_text_to_image(picto, str(legrate) + '%', font_path, font_size, font_color, height, width)
        file_path = './tmp/' + author_id + '.png'
        img.save(file_path)
        return file_path

    def makeScoreImage(self, id: str, tag: str, data, author_id: str):
        baseScoreboardImage = None
        img = None
        for player in data["players"]:
            if player["name"] == id and player["tag"] == tag:
                if player["winlose"] == "Win":
                    if player["team"] == "Blue":
                        baseScoreboardImage = Image.open('./assets/score1rank.png').copy()
                    elif player["team"] == "Red":
                        baseScoreboardImage = Image.open('./assets/score2rank.png').copy()
                elif player["winlose"] == "Lose":
                    if player["team"] == "Blue":
                        baseScoreboardImage = Image.open('./assets/score2rank.png').copy()
                    elif player["team"] == "Red":
                        baseScoreboardImage = Image.open('./assets/score1rank.png').copy()
                else:
                    baseScoreboardImage = Image.open('./assets/score1rank.png').copy()
        font_path = './assets/NotoSansJP-Regular.otf'
        font_size = 35
        font_color = (255,255,255)
        file_path = './tmp/' + author_id + '_score.png'
        agent_file_path = ""
        i = 0
        blueCount = 0   #Upper
        redCount = 0    #Lower
        charaIconX = 10
        charaIconYUpper = 30 + 75*blueCount
        charaIconYLower = 430 + 75*redCount
        nameX = 85
        rankX = 400
        acsX = 500
        killsX = 600
        deathsX = 700
        assistsX = 800
        kdX = 900
        hsrateX = 1000
        econX = 1100
        fbsX = 1240
        strYUpper = 40 + 75*blueCount
        strYLower = 440 + 75*redCount
        for player in data["players"]:
            if player["team"] == "Blue":
                charaIconYUpper = 30 + 75*blueCount
                strYUpper = 40 + 75*blueCount - 10
                name = player["name"]
                chara = player["chara"]
                kills = player["kills"]
                deaths = player["deaths"]
                assists = player["assists"]
                acs = str(player["acs"])
                bodyshots = player["bodyshots"]
                headshots = player["headshots"]
                legshots = player["legshots"]
                rank = player["rank"]
                if bodyshots == None:
                    bodyshots = 0
                if headshots == None:
                    headshots = 0
                if legshots == None:
                    legshots = 0
                total = bodyshots + headshots + legshots
                headrate = str(Decimal(str(headshots / total * 100)).quantize(Decimal(0), rounding=ROUND_HALF_UP))
                kd = kd = str(round(kills/deaths, 1))
                econ = player["econ"]
                fbs = player["fbs"]
                agent_file_path = './assets/chara/' + chara + '.png'
                if chara == "KAY/O":
                    agent_file_path = './assets/chara/KAYO.png'
                agent_file = Image.open(agent_file_path).copy()
                baseScoreboardImage.paste(agent_file,(charaIconX,charaIconYUpper), agent_file)
                rank_file_path = './assets/rank/' + str(rank) + '.png'
                rank_file = Image.open(rank_file_path).copy()
                baseScoreboardImage.paste(rank_file, (rankX, charaIconYUpper), rank_file)
                strCount = 0
                fixedName = ''
                limitedLen = 16
                for c in name:
                    if unicodedata.east_asian_width(c) in 'FWA':
                        strCount += 2
                    else:
                        strCount += 1
                    if strCount > limitedLen:
                        fixedName += '...'
                        break
                    fixedName += c
                #make image
                img = self.add_text_to_image(baseScoreboardImage, fixedName, font_path, font_size, font_color, strYUpper, nameX)
                img = self.add_text_to_image(baseScoreboardImage, acs, font_path, font_size, font_color, strYUpper, acsX)
                img = self.add_text_to_image(baseScoreboardImage, str(kills), font_path, font_size, font_color, strYUpper, killsX)
                img = self.add_text_to_image(baseScoreboardImage, str(deaths), font_path, font_size, font_color, strYUpper, deathsX)
                img = self.add_text_to_image(baseScoreboardImage, str(assists), font_path, font_size, font_color, strYUpper, assistsX)
                img = self.add_text_to_image(baseScoreboardImage, kd, font_path, font_size, font_color, strYUpper, kdX)
                img = self.add_text_to_image(baseScoreboardImage, headrate, font_path, font_size, font_color, strYUpper, hsrateX)
                img = self.add_text_to_image(baseScoreboardImage, str(econ), font_path, font_size, font_color, strYUpper, econX)
                img = self.add_text_to_image(baseScoreboardImage, str(fbs), font_path, font_size, font_color, strYUpper, fbsX)
                blueCount += 1
            else:
                charaIconYLower = 430 + 75*redCount
                strYLower = 440 + 75*redCount - 10
                name = player["name"]
                chara = player["chara"]
                kills = player["kills"]
                deaths = player["deaths"]
                assists = player["assists"]
                acs = str(player["acs"])
                bodyshots = player["bodyshots"]
                headshots = player["headshots"]
                legshots = player["legshots"]
                rank = player["rank"]
                if bodyshots == None:
                    bodyshots = 0
                if headshots == None:
                    headshots = 0
                if legshots == None:
                    legshots = 0
                total = bodyshots + headshots + legshots
                headrate = str(Decimal(str(headshots / total * 100)).quantize(Decimal(0), rounding=ROUND_HALF_UP))
                kd = str(round(kills/deaths, 1))
                econ = player["econ"]
                fbs = player["fbs"]
                agent_file_path = './assets/chara/' + chara + '.png'
                if chara == "KAY/O":
                    agent_file_path = './assets/chara/KAYO.png'
                agent_file = Image.open(agent_file_path).copy()
                baseScoreboardImage.paste(agent_file,(charaIconX,charaIconYLower),agent_file)
                rank_file_path = './assets/rank/' + str(rank) + '.png'
                rank_file = Image.open(rank_file_path).copy()
                baseScoreboardImage.paste(rank_file, (rankX, charaIconYLower), rank_file)
                strCount = 0
                fixedName = ''
                limitedLen = 16
                for c in name:
                    if unicodedata.east_asian_width(c) in 'FWA':
                        strCount += 2
                    else:
                        strCount += 1
                    if strCount > limitedLen:
                        fixedName += '...'
                        break
                    fixedName += c
                #make image
                img = self.add_text_to_image(baseScoreboardImage, fixedName, font_path, font_size, font_color, strYLower, nameX)
                img = self.add_text_to_image(baseScoreboardImage, acs, font_path, font_size, font_color, strYLower, acsX)
                img = self.add_text_to_image(baseScoreboardImage, str(kills), font_path, font_size, font_color, strYLower, killsX)
                img = self.add_text_to_image(baseScoreboardImage, str(deaths), font_path, font_size, font_color, strYLower, deathsX)
                img = self.add_text_to_image(baseScoreboardImage, str(assists), font_path, font_size, font_color, strYLower, assistsX)
                img = self.add_text_to_image(baseScoreboardImage, kd, font_path, font_size, font_color, strYLower, kdX)
                img = self.add_text_to_image(baseScoreboardImage, headrate, font_path, font_size, font_color, strYLower, hsrateX)
                img = self.add_text_to_image(baseScoreboardImage, str(econ), font_path, font_size, font_color, strYLower, econX)
                img = self.add_text_to_image(baseScoreboardImage, str(fbs), font_path, font_size, font_color, strYLower, fbsX)
                redCount += 1
            i = i + 1
            if i == 10:
                break
        img.save(file_path)
        return file_path

    def makeVCTImage(self, id: str, tag: str, data, author_id: str):
        baseVCTImage: Image.Image = None
        maskVCTImage: Image.Image = None
        imageNum = 0
        for player in data["players"]:
            if player["name"] == id and player["tag"] == tag:
                if player["winlose"] == "Win":
                    if player["team"] == "Blue":
                        baseVCTImage = Image.open('./assets/vct/vct1.png').copy()
                        maskVCTImage = Image.open('./assets/vct/vct1mask.png').copy()
                        imageNum = 1
                    elif player["team"] == "Red":
                        baseVCTImage = Image.open('./assets/vct/vct2.png').copy()
                        maskVCTImage = Image.open('./assets/vct/vct2mask.png').copy()
                        imageNum = 2
                elif player["winlose"] == "Lose":
                    if player["team"] == "Blue":
                        baseVCTImage = Image.open('./assets/vct/vct2.png').copy()
                        maskVCTImage = Image.open('./assets/vct/vct2mask.png').copy()
                        imageNum = 2
                    elif player["team"] == "Red":
                        baseVCTImage = Image.open('./assets/vct/vct1.png').copy()
                        maskVCTImage = Image.open('./assets/vct/vct1mask.png').copy()
                        imageNum = 1
                else:
                    baseVCTImage = Image.open('./assets/vct/vct1.png').copy()
                    maskVCTImage = Image.open('./assets/vct/vct1mask.png').copy()
                    imageNum = 1
        Draw = ImageDraw.Draw(baseVCTImage)
        scoreFont = ImageFont.truetype('./assets/Tungsten-Bold.ttf', 175)
        nameMVPFont = ImageFont.truetype('./assets/Tungsten-Bold.ttf', 80)
        subNameMVPFont = ImageFont.truetype('./assets/NotoSansJP-Regular.otf', 70)
        nameFont = ImageFont.truetype('./assets/Tungsten-Bold.ttf', 35)
        subNameFont = ImageFont.truetype('./assets/NotoSansJP-Bold.otf', 25)
        charaMVPFont = ImageFont.truetype('./assets/DINNextLTPro-Regular.ttf', 35)
        charaFont = ImageFont.truetype('./assets/DINNextLTPro-Regular.ttf', 20)
        #Coords
        mvpCharaY = 420

        leftMVPNameX = 430
        rightMVPNameX = 1495
        mvpNameY = 450

        leftMVPKDX = 205
        leftMVPACSX = 375
        leftMVPKILLX = 580
        rightMVPKDX = 1275
        rightMVPACSX = 1440
        rightMVPKILLX = 1650
        mvpStatsY = 560

        leftCharaX = {}
        leftCharaX[0] = 0
        leftCharaX[1] = 105
        leftCharaX[2] = 315
        leftCharaX[3] = 525
        leftCharaX[4] = 735
        rightCharaX = {}
        rightCharaX[0] = 0
        rightCharaX[1] = 985
        rightCharaX[2] = 1195
        rightCharaX[3] = 1405
        rightCharaX[4] = 1615
        CharastrY = 715
        NamestrY = 740
        CharaY = 750
        statsY = 930

        #Coords

        map = data["map"]
        mapPath = './assets/maps/' + map + '.png'

        mapImage: Image.Image = Image.open(mapPath).copy()
        mapImage = self.scaleToWidth(mapImage.crop((420, 0, 1500, 1080)), 300).convert('RGBA')
        baseVCTImage.paste(mapImage, (60, 40), mapImage)

        blueScore = data["blueScore"]
        redScore = data["redScore"]

        blueScoreWidth, blueScoreHeight = Draw.textsize(str(blueScore), font=scoreFont)
        redScoreWidth, redScoreHeight = Draw.textsize(str(redScore), font=scoreFont)
        if imageNum == 1:
            Draw.text((780 - blueScoreWidth / 2, 110), str(blueScore), (13, 180, 150), font=scoreFont)
            Draw.text((1140 - redScoreWidth / 2, 110), str(redScore), (187, 72, 81), font=scoreFont)
        if imageNum == 2:
            Draw.text((780 - blueScoreWidth / 2, 110), str(blueScore), (187, 72, 81), font=scoreFont)
            Draw.text((1140 - redScoreWidth / 2, 110), str(redScore), (13, 180, 150), font=scoreFont)

        blueIndex: int = 0
        redIndex: int = 0
        for playerStat in data["players"]:
            charaFilePath = './assets/charaport/' + playerStat["chara"] + '.png'
            if playerStat["chara"] == "KAY/O":
                charaFilePath = './assets/charaport/KAYO.png'
            charaImage = Image.open(charaFilePath).copy()
            kd = str(round((playerStat["kills"] / playerStat["deaths"]), 1))
            acs = str(playerStat["acs"])
            charaStr = playerStat["chara"].upper()
            name = playerStat["name"]
            strCount = 0
            fixedName = ''
            limitedLen = 16
            twobyteFlag = False
            for c in name:
                if unicodedata.east_asian_width(c) in 'FWA':
                    strCount += 2
                    twobyteFlag = True
                else:
                    strCount += 1
                if strCount > limitedLen:
                    fixedName += '...'
                    break
                fixedName += c
            font = subNameFont if twobyteFlag else nameFont

            #Draw MVPs
            if blueIndex == 0 and playerStat["team"] == 'Blue':
                #trimming the chara image in certain size and paste it
                charaImage = self.scaleToWidth(charaImage, 600)
                charaImage = charaImage.crop((0, 0, 700, 350))
                baseVCTImage.paste(charaImage, (495, 340), charaImage)
                kills = str(playerStat["kills"])
                font = subNameMVPFont if twobyteFlag else nameMVPFont
                fixedNameWidth, fixedNameHeight = Draw.textsize(fixedName, font=font)
                charaStrWidth, charaStrHeight = Draw.textsize(charaStr, font = charaMVPFont)
                Draw.text(((leftMVPNameX - charaStrWidth / 2), mvpCharaY), charaStr, (169, 169, 169), charaMVPFont)
                Draw.text(((leftMVPNameX - fixedNameWidth / 2), mvpNameY), fixedName, (255, 255, 255), font)
                Draw.text((leftMVPKDX, mvpStatsY), kd, (255, 255, 255), nameMVPFont)
                Draw.text((leftMVPACSX, mvpStatsY), acs, (255, 255, 255), nameMVPFont)
                Draw.text((leftMVPKILLX, mvpStatsY), kills, (255, 255, 255), nameMVPFont)
                blueIndex += 1
                continue

            elif redIndex == 0 and playerStat["team"] == 'Red':
                charaImage = self.scaleToWidth(charaImage, 600)
                charaImage = charaImage.crop((0, 0, 700, 350))
                baseVCTImage.paste(charaImage, (805, 340), charaImage)
                kills = str(playerStat["kills"])
                font = subNameMVPFont if twobyteFlag else nameMVPFont
                fixedNameWidth, fixedNameHeight = Draw.textsize(fixedName, font=font)
                charaStrWidth, charaStrHeight = Draw.textsize(charaStr, font = charaMVPFont)
                Draw.text(((rightMVPNameX - charaStrWidth / 2), mvpCharaY), charaStr, (169, 169, 169), charaMVPFont)
                Draw.text(((rightMVPNameX - fixedNameWidth / 2), mvpNameY), fixedName, (255, 255, 255), font)
                Draw.text((rightMVPKDX, mvpStatsY), kd, (255, 255, 255), nameMVPFont)
                Draw.text((rightMVPACSX, mvpStatsY), acs, (255, 255, 255), nameMVPFont)
                Draw.text((rightMVPKILLX, mvpStatsY), kills, (255, 255, 255), nameMVPFont)
                redIndex += 1
                continue

            #Draw others
            elif playerStat["team"] == 'Blue':
                charaImage = self.scaleToWidth(charaImage, 400)
                charaImage = charaImage.crop((100, 0, 300, 400))
                baseVCTImage.paste(charaImage, (leftCharaX[blueIndex], CharaY), charaImage)
                fixedNameWidth, fixedNameHeight = Draw.textsize(fixedName, font=font)
                Draw.text((((leftCharaX[blueIndex] + 100) - fixedNameWidth / 2), NamestrY), fixedName, (255, 255, 255), font)
                charaStrWidth, charaStrHeight = Draw.textsize(charaStr, font = charaFont)
                Draw.text((((leftCharaX[blueIndex] + 100) - charaStrWidth / 2), CharastrY), charaStr, (169, 169, 169), charaFont)
                
                blueIndex += 1
            else:
                charaImage = self.scaleToWidth(charaImage, 400)
                charaImage = charaImage.crop((100, 0, 300, 400))
                baseVCTImage.paste(charaImage, (rightCharaX[redIndex], CharaY), charaImage)
                fixedNameWidth, fixedNameHeight = Draw.textsize(fixedName, font=font)
                Draw.text((((rightCharaX[redIndex] + 100) - fixedNameWidth / 2), NamestrY), fixedName, (255, 255, 255), font)
                charaStrWidth, charaStrHeight = Draw.textsize(charaStr, font = charaFont)
                Draw.text((((rightCharaX[redIndex] + 100) - charaStrWidth / 2), CharastrY), charaStr, (169, 169, 169), charaFont)
                
                redIndex += 1

        baseVCTImage.paste(maskVCTImage, (0, 0), maskVCTImage)

        #Draw acs and kds
        blueIndex = 0
        redIndex = 0
        for playerStat in data["players"]:
            kd = str(round((playerStat["kills"] / playerStat["deaths"]), 1))
            acs = str(playerStat["acs"])
            if blueIndex == 0 and playerStat["team"] == 'Blue':
                blueIndex += 1
                continue
            if redIndex == 0 and playerStat["team"] == 'Red':
                redIndex += 1
                continue
            elif playerStat["team"] == 'Blue':
                try:
                    Draw.text((leftCharaX[blueIndex] + 20, statsY), acs, (255, 255, 255), nameFont)
                    Draw.text((leftCharaX[blueIndex] + 150, statsY), kd, (255, 255, 255), nameFont)
                except Exception as e:
                    print(e)
                blueIndex += 1
            else:
                Draw.text((rightCharaX[redIndex] + 20, statsY), acs, (255, 255, 255), nameFont)
                Draw.text((rightCharaX[redIndex] + 150, statsY), kd, (255, 255, 255), nameFont)
                redIndex += 1

        file_path = './tmp/' + author_id + '_vct.png'
        baseVCTImage.save(file_path)
        return file_path

    def scaleToWidth(self, img: Image.Image, width: int) -> Image.Image:
        height = round(img.height * width / img.width)
        return img.resize((width, height))

    async def onError(self, bot: discord.Bot, funcName: str, exception: Exception) -> None:
        systemLogChannel = bot.get_channel(self.LOG_CHANNEL)
        await systemLogChannel.send('Exception occured while executing command: ' + str(funcName))
        await systemLogChannel.send('Traceback: ' + str(exception))
        return
