import asyncio
import logging
import os
import discord
from discord.ext import commands
import requests

STORAGE_DIR = '.\amiibo'
logging.basicConfig(format='%(levelname)s:%(message)s',
                    level=logging.INFO)
PREFIX = '!'
client = discord.Client()
bot = commands.Bot(command_prefix=PREFIX, description=DESCRIPTION)

def ingest_file(username, nickname):
    filesize = discord.Attachment.size
    filename = discord.Attachment.filename
    url = discord.Attachment.url
    reqobj = requests.get(url, stream=True)
    filename = STORAGE_DIR + str(username.id) + '-' + nickname + '.bin'
    outstring = b''
    with open(filename, 'wb') as writefile:
        for chunk in reqobj.iter_content(chunk_size=50):
            outstring += chunk
        length = len(outstring)
        if length < 540:
            diff = 540 - length
            outstring += b'\x00' * diff
        if length > 540:
            outstring = outstring[:540]
        writefile.write(outstring)



@bot.command(name='help')
async def help_cmd(ctx)
            logging.info("{} - {}".format(ctx.author, ctx.message))
            retmsg = ("This is the AmiiBot help menu!\n"
                      "`!store <amiibo nickname>` (and attach the bin)\n"
                      "`!list`\n"
                      "`!rename <old amiibo nickname>, <new amiibo nickname>`\n"
                      "`!delete <amiibo nickname>`\n"
                      "`!send <Tag the host> <amiibo nickname>`\n"
                      "`!download <amiibonickname>`")
            await ctx.send(retmsg)

@bot.command(name='list')
async def list_cmd(ctx)
            logging.info("{} - {}".format(ctx.author, ctx.message))
            filelist = os.listdir(STORAGE_DIR)
            amiibolist = [x for x in filelist if x.startswith(str(ctx.author.id))]
            namelist = ['-'.join(x.split('-')[1:]).replace('.bin', '') for x in amiibolist]
            print(namelist)
            retmsg = "The amiibo you have stored are:\n" + '\n'.join(namelist)
            await ctx.send(retmsg)

@bot.command(name='delete')
async def delete_cmd(ctx)
            try:
                logging.info("{} - {}".format(ctx.author, ctx.message))
                splitlist = ctx.message.split()
                to_del = '_'.join(splitlist[1:])
                filename = STORAGE_DIR + str(ctx.author.id) + '-' + to_del + '.bin'
                os.remove(filename)
                await ctx.send('Successfully deleted {}'.format(to_del))
            except Exception as exc:
                logging.warning(exc)
                await ctx.send('Deletion Failed')

@bot.command(name='rename')
async def rename_cmd(ctx)
            try:
                logging.info("{} - {}".format(ctx.author, ctx.message))
                arglist = ctx.message.split()[1:]
                argstring = ' '.join(arglist)
                oldname, newname = ['_'.join(x.strip().split()) for x in argstring.split(',')]
                oldfilename = STORAGE_DIR + str(ctx.author.id) + '-' + oldname + '.bin'
                newfilename = STORAGE_DIR + str(ctx.author.id) + '-' + newname + '.bin'
                os.rename(oldfilename, newfilename)
                await ctx.send('Successfully renamed {} to {}'.format(oldname, newname))
            except Exception as exc:
                logging.warning(exc)
                if 'No such file or directory' in str(exc):
                    await ctx.send('File does not exist, make sure your spelling is correct')
                elif 'not enough values to unpack' in str(exc):
                    await ctx.send('Not enough names provided, should be comma separated')
                elif 'too many values to unpack'in str(exc):
                    await ctx.send('Too many names provided, calm down')
                else:
                    await ctx.send('Failed to rename')

@bot.command(name='store')
async def store_cmd(ctx)
            logging.info("{} - {}".format(ctx.author, ctx.message))
            if ctx.message.attachment.size != 540:      #and message.Attachment.url.endswith('bin')
                nick = '_'.join(ctx.message.split()[1:])
                try:
                    ingest_file(ctx.author, nick)
                    await ctx.send('Successfully stored - ' + nick)
                except Exception as exc:
                    logging.warning(exc)
                    await ctx.send('Failed to Store')
            else:
                await ctx.send('Improper bin size')


@bot.command(name='send')
async def send(ctx)
            logging.info("{} - {}".format(ctx.author, ctx.message))
            splitlist = ctx.message.split()
            if len(splitlist) < 3:
                await ctx.send('Improper usage of command, please format it as: `!send <@usertag> <amiibonickname>`')
            else:
                try:
                    to_send = '_'.join(splitlist[2:])
                    recipient = ctx.message.mentions[0]
                    filename = STORAGE_DIR + str(ctx.author.id) + '-' + to_send + '.bin'
                    sendname = str(ctx.author) + '-' + to_send + '.bin'
                    await client.send_file(recipient, filename, filename=sendname)
                    await client.send_message(message.channel, 'Successfully sent {} to {}'.format(to_send, str(recipient)))
                except Exception as exc:
                    logging.warning(exc)
                    if 'Cannot send messages to this user' in str(exc):
                        await ctx.send('Cannot send messages to this user, they may have DMs turned off')
                    elif 'No such file or directory' in str(exc):
                        await ctx.send('File does not exist, make sure your spelling is correct')
                    else:
                        await ctx.send('Failed to Send')


@bot.command(name='download')
async def dl(ctx)
            logging.info("{} - {}".format(message.author, ctx.message))
            splitlist = ctx.message.split()
            amiiname = '_'.join(splitlist[1:])
            if len(splitlist) == 1:
                await client.send_message(message.channel, 'No nickname defined, please try again')
            else:
                try:
                    filename = STORAGE_DIR + str(message.author.id) + '-' + amiiname + '.bin'
                    sendname = str(message.author) + '-' + amiiname + '.bin'
                    await client.send_file(message.author, filename, filename=sendname)
                except Exception as exc:
                    logging.warning(exc)
                    if 'No such file or directory' in str(exc):
                        await client.send_message(message.channel, 'File does not exist, make sure your spelling is correct')
                    else:
                        await client.send_message(message.channel, 'Failed to Download')

@client.event
async def on_ready():
    logging.info('Logged in as')
    logging.info(client.user.name)
    logging.info(client.user.id)
    logging.info('------')


client.run('TOKEN')