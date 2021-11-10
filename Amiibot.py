import asyncio
import logging
import os
import discord
from discord import File
from discord.ext import commands
import requests

PREFIX = "!"
TOKEN = os.environ["token"]
STORAGE_DIR = "./amiibo/"

logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)

bot = commands.Bot(command_prefix=PREFIX)

@bot.event
async def on_ready():
    logging.info("Logged in as")
    logging.info(bot.user.name)
    logging.info(bot.user.id)
    logging.info("------")


bot.remove_command('help')

@bot.command(name="help")
async def help_cmd(ctx):
    logging.info("{} - {}".format(ctx.author, ctx.message))
    retmsg = (
        "This is the AmiiBot help menu!\n"
        "`!store <amiibo nickname>` (and attach the bin)\n"
        "`!list`\n"
        "`!rename <old amiibo nickname>, <new amiibo nickname>`\n"
        "`!delete <amiibo nickname>`\n"
        "`!send <Tag the host> <amiibo nickname>`\n"
        "`!download <amiibonickname>`"
    )
    await ctx.send(retmsg)


@bot.command(name="list")
async def list_cmd(ctx):
    logging.info("{} - {}".format(ctx.author, ctx.message))
    filelist = os.listdir(STORAGE_DIR)
    amiibolist = [x for x in filelist if x.startswith(str(ctx.author.id))]
    namelist = ["-".join(x.split("-")[1:]).replace(".bin", "") for x in amiibolist]
    print(namelist)
    retmsg = "The amiibo you have stored are:\n" + "\n".join(namelist)
    await ctx.send(retmsg)


@bot.command(name="delete")
async def delete_cmd(ctx, to_del):
    try:
        logging.info("{} - {}".format(ctx.author, ctx.message))
        filename = STORAGE_DIR + str(ctx.author.id) + "-" + to_del + ".bin"
        os.remove(filename)
        await ctx.send(f"Successfully deleted {to_del}")
    except Exception as exc:
        logging.warning(exc)
        await ctx.send("Deletion Failed")


@bot.command(name="rename")
async def rename_cmd(ctx, oldname, newname):
    try:
        logging.info("{} - {}".format(ctx.author, ctx.message))
        oldfilename = STORAGE_DIR + str(ctx.author.id) + "-" + oldname + ".bin"
        newfilename = STORAGE_DIR + str(ctx.author.id) + "-" + newname + ".bin"
        os.rename(oldfilename, newfilename)
        await ctx.send("Successfully renamed {} to {}".format(oldname, newname))
    except Exception as exc:
        logging.warning(exc)
        if "No such file or directory" in str(exc):
            await ctx.send("File does not exist, make sure your spelling is correct")
        elif "not enough values to unpack" in str(exc):
            await ctx.send("Not enough names provided, should be comma separated")
        elif "too many values to unpack" in str(exc):
            await ctx.send("Too many names provided, calm down")
        else:
            await ctx.send("Failed to rename")


@bot.command(name="store")
async def store_cmd(ctx, nick):
    logging.info("{} - {}".format(ctx.author, ctx.message))
    if ctx.message.attachments[0].size == 540 and ctx.message.attachments[0].filename.endswith('bin'):
        try:
            filepathname = STORAGE_DIR + str(ctx.author.id) + "-" + nick + ".bin"
            await ctx.message.attachments[0].save(fp=filepathname)
            await ctx.send("Successfully stored - " + nick)
        except Exception as exc:
            logging.warning(exc)
            await ctx.send("Failed to Store")
    else:
        await ctx.send("Improper bin size")


@bot.command(name="send")
async def send(ctx, userid, to_send):
    logging.info("{} - {}".format(ctx.author, ctx.message))
    try:
            user = ctx.message.mentions[0]
            print(user)
            filename = STORAGE_DIR + str(ctx.author.id) + "-" + to_send + ".bin"
            sendname = STORAGE_DIR + to_send + ".bin"
            os.rename(filename, sendname)
            await user.send(file=File(sendname))
            os.rename(sendname, filename)
            await ctx.send(
                "Successfully sent {} to {}".format(to_send, str(user)),
            )
    except Exception as exc:
            logging.warning(exc)
            if "Cannot send messages to this user" in str(exc):
                await ctx.send(
                    "Cannot send messages to this user, they may have DMs turned off"
                )
            elif "No such file or directory" in str(exc):
                await ctx.send(
                    "File does not exist, make sure your spelling is correct"
                )
            else:
                await ctx.send("Failed to Send")

@bot.command(name="download")
async def dl(ctx, amiiname):
    logging.info("{} - {}".format(ctx.author, ctx.message))
    try:
            filename = STORAGE_DIR + str(ctx.author.id) + "-" + amiiname + ".bin"
            sendname = STORAGE_DIR + amiiname + ".bin"
            os.rename(filename, sendname)
            await ctx.send(file=File(sendname))
            os.rename(sendname, filename)
    except Exception as exc:
            logging.warning(exc)
            if "No such file or directory" in str(exc):
                await ctx.send(
                    "File does not exist, make sure your spelling is correct"
                )
            else:
                await ctx.send("Failed to Download")




loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(
        bot.start(TOKEN)
    )
except KeyboardInterrupt:
    loop.run_until_complete(bot.close())
