import discord
from discord.ext import commands
from discord.ext.commands.context import Context
from discord.member import Member
import logging
from dotenv import load_dotenv
import os
from Game import Game
from typing import Optional

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
logging.getLogger('discord.http').setLevel(logging.INFO)
log_handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
dt_fmt = '%Y-%m-%d %H:%M:%S'
log_formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
log_handler.setFormatter(log_formatter)
logger.addHandler(log_handler)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)
bot.remove_command("help") # replacing the default with our own

game: Optional[Game] = None

load_dotenv()
token = os.getenv('DISCORD_TOKEN')
if token is None:
    logger.error("Unable to load token from env!")
    quit()

@bot.event
async def on_ready():
    logger.info("Ready.")
    target_guild_id = os.getenv('TARGET_GUILD_ID')
    if target_guild_id is None:
        logger.error("Unable to load guild id from env!")
        quit()

    guild = bot.get_guild(int(target_guild_id))
    if guild is None:
        logger.error("Unable to get guild from guild id!")
        quit()
    
    global game
    game = Game(list(guild.members))
    print("Game initialized.")
    logger.info("Game initialized.")

@bot.command()
async def help(ctx: Context):
    message = (
        "- Join the game using !join.\n"
        "- To leave, use !leave.\n"
        "- Once everyone's ready, anyone can start the game with !start.\n"
        "- The game master can end the game with !end.\n"
        "- Each player takes turns trying to determine their role by asking yes or no questions to the other players.\n"
        "- If it is not your turn, you must answer and can only do so with \"yes\" or \"no\". You cannot lie.\n"
        "- The winner is whomever has the most fun.\n"
        "**Important notes**\n"
        "- You will need to allow DMs from users of mutual servers so the bot can DM you.\n"
        "- After the game starts, no new players can join without resetting the game.\n"
        "- Role assignments cannot change once the game has started.\n"
        "- All role information should be kept private until revealed through gameplay with the exception of jokes that are *very* funny."
    )
    await ctx.reply(message)
    return

@bot.command()
async def join(ctx: Context):
    if game is None:
        await ctx.send(f"Game is not yet initialized. Please wait. {ctx.author.name}")
        logger.error(f"Join attempted before game initialized by {ctx.author.name}!")
        return
    if ctx.guild is None:
        await ctx.send(f"Unable to locate guild. {ctx.author.name}")
        logger.error("Join attempted from a user whos guild is None!")
        return

    member = await ctx.guild.fetch_member(ctx.author.id)
    if member is None:
        await ctx.reply(f"Unable to locate member.")
        logger.error(f"Join attempted from member {ctx.author.name} who could not be located!")
        return

    if game.add_player(member):
        logger.info(f"Added player {ctx.author.name}")
        names = [player.display_name for player in game.get_players()]
        msg = f"{ctx.author.name} has joined. Current players are: {names}"
        await ctx.reply(msg)
    else:
        logger.error(f"Failed to add player {ctx.author.name}")
    return

@bot.command()
async def leave(ctx: Context):
    if game is None:
        await ctx.send(f"Game is not yet initialized. Please wait. {ctx.author.name}")
        logger.error(f"Leave attempted before game initialized by {ctx.author.name}!")
        return
    if ctx.guild is None:
        await ctx.send(f"Unable to locate guild. {ctx.author.name}")
        logger.error("Leave attempted from a user whos guild is None!")
        return
    
    member = await ctx.guild.fetch_member(ctx.author.id)
    if member is None:
        await ctx.reply(f"Unable to locate member.")
        logger.error(f"Join attempted from member {ctx.author.name} who could not be located!")
        return
    
    if game.remove_player(member):
        logger.info(f"Removed player {ctx.author.name}")
        names = [player.display_name for player in game.get_players()]
        msg = f"{ctx.author.name} has left. Current players are: {names}"
        await ctx.reply(msg)
    else:
        await ctx.reply(f"Unable to leave.")
        logger.error(f"Failed to remove player {ctx.author.name}")
    return

@bot.command()
async def start(ctx: Context):
    if game is None:
        await ctx.send(f"Game is not yet initialized! Please wait. {ctx.author.name}")
        logger.error(f"Start attempted before game initialized by {ctx.author.name}!")
        return
    
    try:
        game.start()
    except:
        await ctx.reply("Not enough players! Canceling game start.")
        logger.error(f"Game start attempted with too few members by {ctx.author.name}")
        return
    
    players = game.get_players()
    for p in players:
        board = game.get_board(p)
        lines = []
        for other in board:
            lines.append(f"player {other.display_name} has role {board.get(other)}")
        msg = "\n".join(lines)
        try:
            await p.send(msg)
            logger.info(f"Sent message \'{msg}\' to {p.name}")
        except discord.Forbidden:
            await ctx.send(f"Unable to send DM to {p.display_name}! Canceling game start.")
            logger.error(f"Unable to send DM to {p.name}!")
            return
    await ctx.reply("Game has been started! Check your DMs.")
    logger.info(f"Game started by {ctx.author.name}.")
    return

@bot.command()
async def end(ctx: Context):
    if game is None:
        await ctx.send(f"Game is not yet initialized! Please wait. {ctx.author.name}")
        logger.error(f"End attempted before game initialized by {ctx.author.name}!")
        return
    game.end()
    await ctx.send(f"The game has been ended, and the players have been reset.")
    logger.info(f"Game ended by {ctx.author.name}")

bot.run(token, log_handler=None)