import discord
import os
import asyncio
import requests
import creds

client = discord.Client()

def ingest_file(attachobj, username, nickname):
    filesize = attachobj['size']
    filename = attachobj['filename']
    url = attachobj['url']
    reqobj = requests.get(url, stream=True)
    filename = str(username) + '-' + nickname + '.bin'
    outstring = b''
    with open(filename, 'wb') as writefile:
        for chunk in reqobj.iter_content(chunk_size=50):
            outstring += chunk
        length = len(outstring)
        print(len(outstring))
        if length < 540:
            diff = 540 - length
            outstring += b'\x00' * diff
        if length > 540:
            outstring = outstring[:540]
        print(len(outstring))
        writefile.write(outstring)



@client.event
async def on_message(message):
    if message.author == client.user:
        return
    else:

        cont = message.content.lower()

        if cont.startswith('!submit'):
            if message.attachments:
                attach = message.attachments[0]
                if attach['size'] in [572, 540, 532] and attach['filename'].endswith('bin'):
                    nick = cont.split()[1]
                    try:
                        ingest_file(attach, message.author, nick)
                        await client.send_message(message.channel, 'Successfully submitted - ' + nick)
                    except Exception as exc:
                        print(exc)
                        await client.send_message(message.channel, 'Failed to Submit')
            else:
                await client.send_message(message.channel, 'No files attached, you must attach a file to submit it.')


        if cont.startswith('!send'):
            splitlist = cont.split()
            if len(splitlist) != 3:
                await client.send_message(message.channel, 'Improper send command, please format it like: `!send <@usertag> <amiibonickname>')
            else:
                to_send = splitlist[2]
                recipient = message.mentions[0]
                filename = str(message.author) + '-' + to_send + '.bin'
                await client.send_file(recipient, filename)
            print(cont.split())


        if cont.startswith('!download'):
            splitlist = cont.split()
            amiilist = splitlist[1:]
            if len(amiilist) > 3:
                await client.send_message(message.channel, 'For rate limiting reasons, you are only able to download three amiibo at a time')
            else:
                for amiibo in amiilist:
                    filename = str(message.author) + '-' + amiibo + '.bin'
                    await client.send_file(message.channel, filename)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    os.makedirs('amiibo', exist_ok=True)


client.run(creds.GimmeCreds())
