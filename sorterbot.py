import discord
from discord.ext import commands

# Initialize bot with intents
intents = discord.Intents.default()
intents.messages = True
intents.reactions = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Global dictionary to track messages and their reactions
tracked_messages = {}

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    # Get the 'screenshots' server
    guild = discord.utils.get(bot.guilds, name="screenshots")
    if guild:
        system_channel = await guild.system_channel
        if system_channel: # Check if system channel exists
            try:
                await system_channel.send("**Hello screenshots server!**\n"
                                        "I'm ready to assist you with some helpful commands:\n"
                                        "- **!help:** Displays a list of available commands.\n")
            except discord.HTTPException as e:
                print(f"Failed to send message to system channel: {e}")
        else:
            print("System channel not found.")
    else:
        print("Guild 'screenshots' not found.")


@bot.event
async def on_message(message):
    # Skip messages from bots
    if message.author.bot:
        return

    # Track all messages, including attachments
    tracked_messages[message.id] = {
        "message": message,
        "reactions": {}
    }

    # Process other commands
    await bot.process_commands(message)

@bot.event
async def on_reaction_add(reaction, user):
    # Skip reactions from bots
    if user.bot:
        return

    # Update reaction counts for tracked messages
    try:
        if reaction.message.id in tracked_messages:
            tracked_messages[reaction.message.id]["reactions"][str(reaction.emoji)] = reaction.count
    except Exception as e:
        print(f"An error occurred while processing reaction: {e}")

@bot.command(name='sort')
async def sort_posts(ctx):
    """Sorts image posts in the current channel by reactions and adds the original reactions to the sorted posts."""
    await ctx.send("Fetching and sorting image posts by reactions...")

    local_tracked_messages = {} # Local tracked messages for this command

    try:
        async for message in ctx.channel.history(limit=None):
            if message.attachments:
                for attachment in message.attachments:
                    if attachment.content_type.startswith('image/'):
                        local_tracked_messages[message.id] = {
                            "message": message,
                            "reactions": {}
                        }
                        for reaction in message.reactions:
                            local_tracked_messages[message.id]["reactions"][str(reaction.emoji)] = reaction.count
                        break # if at least one attachment is an image, it is enough.
    except discord.Forbidden:
        await ctx.send("I don't have permission to read message history in this channel.")
        return
    except discord.HTTPException as e:
        await ctx.send(f"An error occurred while fetching messages: {e}")
        return

    if not local_tracked_messages:
        await ctx.send("No image posts found to sort!")
        return

    sorted_messages = sorted(
        local_tracked_messages.values(),
        key=lambda m: sum(m["reactions"].values())
    )

    sorted_channel = discord.utils.get(ctx.guild.channels, name="sorted_posts")
    if not sorted_channel:
        try:
            sorted_channel = await ctx.guild.create_text_channel("sorted_posts")
        except discord.HTTPException as e:
            print(f"Failed to create sorted_posts channel: {e}")
            await ctx.send("Failed to create sorted_posts channel.")
            return

    await sorted_channel.send("Image posts sorted by reactions:")
    for entry in sorted_messages:
        message = entry["message"]
        content_to_send = ""
        if message.content:
            content_to_send += message.content + "\n"
        if message.attachments:
            for attachment in message.attachments:
                if attachment.content_type.startswith('image/'):
                    content_to_send += f"Attachment: {attachment.url}\n"

        sent_message = None

        if content_to_send:
            sent_message = await sorted_channel.send(content_to_send)
        else:
            sent_message = await sorted_channel.send("Message had no content or attachments.")

        if sent_message:
            for reaction in message.reactions:
                try:
                    await sent_message.add_reaction(reaction.emoji)
                except discord.HTTPException as e:
                    print(f"Failed to add reaction {reaction.emoji} to sorted message: {e}")

@bot.command(name='delete_all')
@commands.has_permissions(manage_messages=True)
async def delete_all(ctx):
    """Deletes all posts in the current channel."""
    await ctx.send("Deleting all messages in this channel...")

    try:
        deleted = await ctx.channel.purge(limit=None)
        await ctx.send(f"Deleted {len(deleted)} messages.")
    except discord.Forbidden:
        await ctx.send("I don't have permission to delete messages in this channel.")
    except discord.HTTPException as e:
        await ctx.send(f"Failed to delete messages: {e}")

@bot.command(name='ping', help='Checks the bot\'s latency.')
async def ping(ctx):
    await ctx.send(f'Pong! Latency: {round(bot.latency * 1000)}ms')

# Replace with your bot token
bot.run("YOUR_BOT_TOKEN")
