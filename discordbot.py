import discord
import os
from dotenv import load_dotenv

from utils.fetch import Fetch
from utils.sheet import Sheet

load_dotenv()

TOKEN = os.environ['DISCORD_TOKEN']
LOG_CHANNEL = int(os.environ['DISCORD_LOG_CHANNEL'])
bot = discord.Bot()

sheet = Sheet()
fetch = Fetch()

@bot.event
async def on_ready():
    print('Ready')
    systemLogChannel = bot.get_channel(LOG_CHANNEL)
    await fetch.updateRiotId(sheet=sheet, channel=systemLogChannel)

if __name__ == '__main__':
    for file in os.listdir('./cogs'):
        if file.endswith('.py'):
            bot.load_extension(f'cogs.{file[:-3]}')
    bot.run(TOKEN)