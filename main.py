import discord
from discord.ext import commands
from typing import Optional
import json
import os
from lock import lock_channel, unlock_channel
from afk import afk_command, handle_message
from snipe import snipe_command, clearsnipe_command, track_message_delete

# Load emojis from JSON
with open('emojis.json', 'r') as f:
    emojis_data = json.load(f)
    EMOJIS = emojis_data['emojis']

# Bot setup with comma prefix
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.guild_messages = True

bot = commands.Bot(command_prefix=',', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.event
async def on_message(message):
    await handle_message(message)
    await bot.process_commands(message)

@bot.event
async def on_message_delete(message):
    await track_message_delete(message)

@bot.command(name='lock', aliases=['l'], description='Lock a channel')
async def lock_cmd(ctx, channel: Optional[discord.TextChannel] = None):
    """Lock a channel - prevents members from sending messages"""
    await lock_channel(ctx, channel)

@bot.command(name='unlock', aliases=['ul'], description='Unlock a channel')
async def unlock_cmd(ctx, channel: Optional[discord.TextChannel] = None):
    """Unlock a channel - allows members to send messages"""
    await unlock_channel(ctx, channel)

@bot.command(name='afk', description='Mark yourself as AFK')
async def afk_cmd(ctx, *, status=None):
    """Mark user as AFK with optional custom status"""
    await afk_command(ctx, status)

@bot.command(name='snipe', aliases=['s'], description='View deleted messages')
async def snipe_cmd(ctx, page: int = 1):
    """View deleted messages in the current channel"""
    await snipe_command(ctx, page)

@bot.command(name='clearsnipe', aliases=['cs'], description='Clear all deleted messages')
async def clearsnipe_cmd(ctx):
    """Clear all deleted messages in the current channel"""
    await clearsnipe_command(ctx)

def main():
    # Get bot token from environment variable
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        print("Error: DISCORD_BOT_TOKEN environment variable not set")
        return
    
    bot.run(token)

if __name__ == '__main__':
    main()
