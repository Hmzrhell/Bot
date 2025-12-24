import discord
import json

def load_locks():
    """Load lock configuration from lock.json"""
    try:
        with open('lock.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"locked_channels": {}}

def save_locks(locks):
    """Save lock configuration to lock.json"""
    with open('lock.json', 'w') as f:
        json.dump(locks, f, indent=2)

def load_emojis():
    """Load emojis from emojis.json"""
    try:
        with open('emojis.json', 'r') as f:
            data = json.load(f)
            return data['emojis']
    except FileNotFoundError:
        return {}

async def send_error_embed(ctx, emoji_name, title):
    """Send error embed in the specified style with custom emoji"""
    emojis = load_emojis()
    emoji_id = emojis.get(emoji_name)
    
    # Create emoji string from ID
    emoji_str = f"<:custom:{emoji_id}>" if emoji_id else "❌"
    
    embed = discord.Embed(
        description=f"{emoji_str} {ctx.author.mention}: {title}",
        color=discord.Color.yellow()
    )
    embed.set_footer(text="")
    await ctx.send(embed=embed)

async def lock_channel(ctx):
    """Lock the current channel - prevents members from sending messages"""
    # Check if user has manage_channels permission
    if not ctx.author.guild_permissions.manage_channels:
        await send_error_embed(ctx, "warn", "You're **missing** permission: `manage_channels`")
        return
    
    try:
        channel = ctx.channel
        guild = channel.guild
        
        # Check if bot has manage_channels permission
        if not guild.me.guild_permissions.manage_channels:
            await send_error_embed(ctx, "warn", "I'm **missing** permission: `manage_channels`")
            return
        
        # Get @everyone role
        everyone_role = guild.default_role
        
        # Lock the channel by denying send_messages permission to @everyone
        await channel.set_permissions(
            everyone_role,
            send_messages=False,
            reason=f"Channel locked by {ctx.author}"
        )
        
        # Save lock state to lock.json
        locks = load_locks()
        locks["locked_channels"][str(channel.id)] = {
            "channel_name": channel.name,
            "locked_by": str(ctx.author),
            "guild_id": guild.id
        }
        save_locks(locks)
        
        # React with lock emoji only
        await ctx.message.add_reaction('🔒')
        
    except discord.Forbidden:
        await send_error_embed(ctx, "warn", "I'm **missing** permission: `manage_channels`")
    except Exception as e:
        print(f"Error locking channel: {e}")
        await send_error_embed(ctx, "warn", f"An error occurred: {str(e)}")

async def unlock_channel(ctx):
    """Unlock the current channel - allows members to send messages"""
    # Check if user has manage_channels permission
    if not ctx.author.guild_permissions.manage_channels:
        await send_error_embed(ctx, "warn", "You're **missing** permission: `manage_channels`")
        return
    
    try:
        channel = ctx.channel
        guild = channel.guild
        
        # Check if bot has manage_channels permission
        if not guild.me.guild_permissions.manage_channels:
            await send_error_embed(ctx, "warn", "I'm **missing** permission: `manage_channels`")
            return
        
        # Get @everyone role
        everyone_role = guild.default_role
        
        # Unlock the channel by allowing send_messages permission to @everyone
        await channel.set_permissions(
            everyone_role,
            send_messages=True,
            reason=f"Channel unlocked by {ctx.author}"
        )
        
        # Remove lock state from lock.json
        locks = load_locks()
        if str(channel.id) in locks["locked_channels"]:
            del locks["locked_channels"][str(channel.id)]
        save_locks(locks)
        
        # React with unlock emoji only
        await ctx.message.add_reaction('🔓')
        
    except discord.Forbidden:
        await send_error_embed(ctx, "warn", "I'm **missing** permission: `manage_channels`")
    except Exception as e:
        print(f"Error unlocking channel: {e}")
        await send_error_embed(ctx, "warn", f"An error occurred: {str(e)}")
