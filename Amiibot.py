import asyncio
import logging
import os
import discord
import requests
import creds

STORAGE_DIR = '/amiibo/'
logging.basicConfig(format='%(levelname)s:%(message)s',
                    filename=STORAGE_DIR+'log.log',
                    level=logging.INFO)

client = discord.Client()

def ingest_file(attachobj, username, nickname):
    filesize = attachobj['size']
    filename = attachobj['filename']
    url = attachobj['url']
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




@client.event
async def on_message(message):
    if message.author == client.user:
        return
    else:

        cont = message.content.lower()

        if cont.startswith('!help'):
            logging.info("{} - {}".format(message.author, cont))
            retmsg = ("This is the AmiiBot help menu!\n"
                      "`!store <amiibo nickname>` (and attach the bin)\n"
                      "`!list`\n"
                      "`!rename <old amiibo nickname>, <new amiibo nickname>`\n"
                      "`!delete <amiibo nickname>`\n"
                      "`!send <Tag the host> <amiibo nickname>`\n"
                      "`!download <amiibonickname>`")
            await client.send_message(message.channel, retmsg)

        if cont.startswith('!list'):
            logging.info("{} - {}".format(message.author, cont))
            filelist = os.listdir(STORAGE_DIR)
            amiibolist = [x for x in filelist if x.startswith(str(message.author.id))]
            namelist = ['-'.join(x.split('-')[1:]).replace('.bin', '') for x in amiibolist]
            print(namelist)
            retmsg = "The amiibo you have stored are:\n" + '\n'.join(namelist)
            await client.send_message(message.author, retmsg)

        if cont.startswith('!delete'):
            try:
                logging.info("{} - {}".format(message.author, cont))
                splitlist = cont.split()
                to_del = '_'.join(splitlist[1:])
                filename = STORAGE_DIR + str(message.author.id) + '-' + to_del + '.bin'
                os.remove(filename)
                await client.send_message(message.channel, 'Successfully deleted {}'.format(to_del))
            except Exception as exc:
                logging.warning(exc)
                await client.send_message(message.channel, 'Deletion Failed')

        if cont.startswith('!rename'):
            try:
                logging.info("{} - {}".format(message.author, cont))
                arglist = cont.split()[1:]
                argstring = ' '.join(arglist)
                oldname, newname = ['_'.join(x.strip().split()) for x in argstring.split(',')]
                oldfilename = STORAGE_DIR + str(message.author.id) + '-' + oldname + '.bin'
                newfilename = STORAGE_DIR + str(message.author.id) + '-' + newname + '.bin'
                os.rename(oldfilename, newfilename)
                await client.send_message(message.channel, 'Successfully renamed {} to {}'.format(oldname, newname))
            except Exception as exc:
                logging.warning(exc)
                if 'No such file or directory' in str(exc):
                    await client.send_message(message.channel, 'File does not exist, make sure your spelling is correct')
                elif 'not enough values to unpack' in str(exc):
                    await client.send_message(message.channel, 'Not enough names provided, should be comma separated')
                elif 'too many values to unpack'in str(exc):
                    await client.send_message(message.channel, 'Too many names provided, calm down')
                else:
                    await client.send_message(message.channel, 'Failed to rename')

        if cont.startswith('!store'):
            logging.info("{} - {}".format(message.author, cont))
            if message.attachments:
                attach = message.attachments[0]
                if attach['size'] in [572, 540, 532] and attach['filename'].endswith('bin'):
                    nick = '_'.join(cont.split()[1:])
                    try:
                        ingest_file(attach, message.author, nick)
                        await client.send_message(message.channel, 'Successfully stored - ' + nick)
                    except Exception as exc:
                        logging.warning(exc)
                        await client.send_message(message.channel, 'Failed to Store')
                else:
                    await client.send_message(message.channel, 'Improper bin size')
            else:
                await client.send_message(message.channel, 'No files attached, you must attach a file to submit it.')


        if cont.startswith('!send'):
            logging.info("{} - {}".format(str(message.author), cont))
            splitlist = cont.split()
            if len(splitlist) < 3:
                await client.send_message(message.channel, 'Improper send command, please format it like: `!send <@usertag> <amiibonickname>`')
            else:
                try:
                    to_send = '_'.join(splitlist[2:])
                    recipient = message.mentions[0]
                    filename = STORAGE_DIR + str(message.author.id) + '-' + to_send + '.bin'
                    sendname = str(message.author) + '-' + to_send + '.bin'
                    await client.send_file(recipient, filename, filename=sendname)
                    await client.send_message(message.channel, 'Successfully sent {} to {}'.format(to_send, str(recipient)))
                except Exception as exc:
                    logging.warning(exc)
                    if 'Cannot send messages to this user' in str(exc):
                        await client.send_message(message.channel, 'Cannot send messages to this user, they may have DMs turned off')
                    elif 'No such file or directory' in str(exc):
                        await client.send_message(message.channel, 'File does not exist, make sure your spelling is correct')
                    else:
                        await client.send_message(message.channel, 'Failed to Send')


        if cont.startswith('!download'):
            logging.info("{} - {}".format(message.author, cont))
            splitlist = cont.split()
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


client.run(creds.GimmeCreds())
