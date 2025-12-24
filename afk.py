import discord
import json
from datetime import datetime

def load_emojis():
    """Load emojis from emojis.json"""
    try:
        with open('emojis.json', 'r') as f:
            data = json.load(f)
            return data['emojis']
    except FileNotFoundError:
        return {}

def load_afk_data():
    """Load AFK user data from afk_data.json"""
    try:
        with open('afk_data.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_afk_data(data):
    """Save AFK user data to afk_data.json"""
    with open('afk_data.json', 'w') as f:
        json.dump(data, f, indent=2)

async def send_afk_embed(ctx, status="AFK"):
    """Send AFK embed with approve emoji"""
    emojis = load_emojis()
    emoji_id = emojis.get("approve")
    
    # Create emoji string from ID
    emoji_str = f"<:custom:{emoji_id}>" if emoji_id else "✅"
    
    embed = discord.Embed(
        description=f"{emoji_str} {ctx.author.mention}: You're now AFK with the status: **{status}**",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

async def afk_command(ctx, status=None):
    """Mark user as AFK with optional custom status"""
    try:
        # Use custom status if provided, otherwise default to AFK
        afk_status = status if status else "AFK"
        
        # Save AFK data
        afk_data = load_afk_data()
        afk_data[str(ctx.author.id)] = {
            "status": afk_status,
            "timestamp": datetime.now().isoformat()
        }
        save_afk_data(afk_data)
        
        await send_afk_embed(ctx, afk_status)
    except Exception as e:
        print(f"Error in AFK command: {e}")

async def handle_message(message):
    """Handle welcome back message for AFK users and AFK notifications"""
    if message.author.bot:
        return
    
    afk_data = load_afk_data()
    user_id = str(message.author.id)
    
    # Check if user is replying to or mentioning an AFK user
    replied_user_id = None
    if message.reference:
        try:
            replied_message = await message.channel.fetch_message(message.reference.message_id)
            replied_user_id = str(replied_message.author.id)
            
            # Check if replied user is AFK
            if replied_user_id in afk_data:
                afk_info = afk_data[replied_user_id]
                afk_datetime = datetime.fromisoformat(afk_info["timestamp"])
                now = datetime.now()
                time_diff = now - afk_datetime
                total_seconds = int(time_diff.total_seconds())
                
                # Format time display
                if total_seconds < 60:
                    time_display = f"{total_seconds} seconds ago"
                else:
                    minutes = total_seconds // 60
                    seconds = total_seconds % 60
                    time_display = f"{minutes} minutes and {seconds} seconds ago"
                
                # Send AFK notification embed
                embed = discord.Embed(
                    description=f"💤 <@{replied_user_id}> is AFK: **{afk_info['status']}** - {time_display}",
                    color=discord.Color.from_rgb(79, 84, 92)
                )
                await message.channel.send(embed=embed)
                return
        except Exception as e:
            print(f"Error checking replied message: {e}")
    
    # Check if mentioning an AFK user
    for mentioned_user in message.mentions:
        mentioned_user_id = str(mentioned_user.id)
        if mentioned_user_id in afk_data:
            afk_info = afk_data[mentioned_user_id]
            afk_datetime = datetime.fromisoformat(afk_info["timestamp"])
            now = datetime.now()
            time_diff = now - afk_datetime
            total_seconds = int(time_diff.total_seconds())
            
            # Format time display
            if total_seconds < 60:
                time_display = f"{total_seconds} seconds ago"
            else:
                minutes = total_seconds // 60
                seconds = total_seconds % 60
                time_display = f"{minutes} minutes and {seconds} seconds ago"
            
            # Send AFK notification embed
            embed = discord.Embed(
                description=f"💤 <@{mentioned_user_id}> is AFK: **{afk_info['status']}** - {time_display}",
                color=discord.Color.from_rgb(79, 84, 92)
            )
            await message.channel.send(embed=embed)
            return
    
    # Check if user is AFK (returning)
    if user_id in afk_data:
        # Calculate time away
        afk_time = afk_data[user_id]["timestamp"]
        afk_datetime = datetime.fromisoformat(afk_time)
        now = datetime.now()
        time_diff = now - afk_datetime
        
        # Get minutes and seconds
        total_seconds = int(time_diff.total_seconds())
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        
        # Send welcome back embed
        embed = discord.Embed(
            description=f"👋 {message.author.mention}: Welcome back, you were away for **{minutes} minutes and {seconds} seconds**",
            color=discord.Color.from_rgb(79, 84, 92)
        )
        await message.channel.send(embed=embed)
        
        # Remove user from AFK list
        del afk_data[user_id]
        save_afk_data(afk_data)
