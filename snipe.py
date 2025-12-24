import discord
import json
from datetime import datetime

def load_deleted_messages():
    """Load deleted messages from deleted.json"""
    try:
        with open('deleted.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_deleted_messages(data):
    """Save deleted messages to deleted.json"""
    with open('deleted.json', 'w') as f:
        json.dump(data, f, indent=2)

async def track_message_delete(message):
    """Track deleted messages"""
    if message.author.bot or not message.content:
        return
    
    deleted_data = load_deleted_messages()
    channel_id = str(message.channel.id)
    
    if channel_id not in deleted_data:
        deleted_data[channel_id] = []
    
    # Get avatar URL with proper format
    avatar_url = str(message.author.avatar.url) if message.author.avatar else None
    
    # Add deleted message
    deleted_data[channel_id].insert(0, {
        "author": message.author.name,
        "author_id": str(message.author.id),
        "avatar_url": avatar_url,
        "content": message.content,
        "timestamp": datetime.now().isoformat()
    })
    
    # Keep only last 10 deleted messages per channel
    if len(deleted_data[channel_id]) > 10:
        deleted_data[channel_id] = deleted_data[channel_id][:10]
    
    save_deleted_messages(deleted_data)

async def snipe_command(ctx, page=1):
    """Show deleted message from the current channel"""
    try:
        deleted_data = load_deleted_messages()
        channel_id = str(ctx.channel.id)
        
        # Check if there are deleted messages in this channel
        if channel_id not in deleted_data or not deleted_data[channel_id]:
            embed = discord.Embed(
                description=f"🔍 {ctx.author.mention}: No deleted messages found!",
                color=discord.Color.yellow()
            )
            await ctx.send(embed=embed)
            return
        
        messages = deleted_data[channel_id]
        total_pages = len(messages)
        
        # Validate page number
        if page < 1 or page > total_pages:
            embed = discord.Embed(
                description=f"🔍 {ctx.author.mention}: Invalid page number. Valid pages: 1-{total_pages}",
                color=discord.Color.yellow()
            )
            await ctx.send(embed=embed)
            return
        
        # Get the message at the requested page
        deleted_msg = messages[page - 1]
        
        # Calculate time ago
        msg_datetime = datetime.fromisoformat(deleted_msg["timestamp"])
        now = datetime.now()
        time_diff = now - msg_datetime
        total_seconds = int(time_diff.total_seconds())
        
        # Format time display
        if total_seconds < 60:
            time_display = f"{total_seconds} seconds"
        else:
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            time_display = f"{minutes}m {seconds}s"
        
        # Create embed with deleted message and avatar
        embed = discord.Embed(
            description=deleted_msg["content"],
            color=discord.Color.from_rgb(128, 128, 128)
        )
        
        # Set author with avatar if available
        author_name = deleted_msg["author"]
        avatar_url = deleted_msg.get("avatar_url")
        
        if avatar_url:
            embed.set_author(name=author_name, icon_url=avatar_url)
        else:
            embed.set_author(name=author_name)
        
        embed.set_footer(text=f"Deleted {time_display} ago • {page}/{total_pages}")
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        print(f"Error in snipe command: {e}")
        embed = discord.Embed(
            description="🔍 An error occurred while retrieving the deleted message.",
            color=discord.Color.yellow()
        )
        await ctx.send(embed=embed)
