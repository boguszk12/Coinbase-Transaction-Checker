import time,discord,requests,os,asyncio,json,imaplib,aiohttp,email
from random import choice                         #importowanie biblioteki discorda
from discord.ext import commands,tasks
from discord.utils import get
from coinbase.wallet.client import Client
from discord import Permissions
from bs4 import BeautifulSoup as bs
from bs4 import NavigableString, Tag

#@commands.has_any_role('Admin','Support')

role_done = 'Support'
welcome_message = 'Welcome to our server!'

generalrgb = discord.Colour.from_rgb(2,149,199)
footer = ''

host = 'imap.gmail.com'
user_n,passw  = '','' #crudentials for email where paypal transactions are sent

btc_add = 'btc_test'
eth_add = 'eth_test'

notification_channel = #notification channel id

money_check = 2 #by how much do you want your transactions to differ

owner_id = #id of guild owner

api_key,api_secret = '', '' #for coinbase

client = commands.Bot(command_prefix= 'cb.')     
client2 = Client(api_key, api_secret)


@client.event  
async def on_ready():                  
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Checking Coinbase!"))
    get_messages.start()
    sending_messages.start()
    #paypal_check.start()
    print('ready')


@client.event
async def on_guild_channel_create(channel):
    if 'ticket' in channel.name:
        time.sleep(1)
        await channel.purge(limit=1)
        embed = discord.Embed(
                title=f"Hello!", 
                description=f"Here is our shop offer! ",
                colour = discord.Colour.from_rgb(21,82,239))
        i = 1
        with open('products.txt','r', encoding='utf-8') as loops:
            for loop in loops:
                loop = loop.split('||')
                embed.add_field(name=f'{i}. {loop[0]}', value=f"`{loop[1]}`", inline = True)
                i+=1
        embed.add_field(name=f'To pay for a product write without [] brackets :', value=f"`cb.pay [product number] [quantity]`", inline = False)
        embed.add_field(name=f'Example :', value=f"`cb.pay 2 1`", inline = False)
        embed.set_footer(text =footer )
        await channel.send(content = None, embed=embed)

async def send_products(channel_id,channelapp):
    with open('orders.txt','r')as ord:
        c = ord.readlines()
        for line in c:
            if str(channel_id) in line.strip():
                i = line.split('||')
                embed = discord.Embed(
                    title=f'Here is your product!' , 
                    description=f"Your order is {i[1]} of {i[0]}",
                    colour = discord.Colour.from_rgb(21,82,239))
                #embed.set_thumbnail(url=welcome_th)
                print('ues')
                with open(f'pr/{i[0]}.txt', 'r') as tr:
                    tr = tr.readlines()
                    for u in range(0,int(i[1])):
                        tr1 = tr[u].rstrip()
                        embed.add_field(name='Product :', value =f'`{tr1}`', inline = True)
                        print(tr)
                        await channelapp.send(tr1)
                        tr.remove(tr[u])
                embed.add_field(name='Important', value =f'**Please do leave a vouch in #vouches-commands if you like our product**', inline = True)
                with open(f'pr/{i[0]}.txt', 'w') as tr2:
                    tr2.write(''.join(tr))
                embed.set_footer(text =footer )
                await channelapp.send(embed=embed, content = None)
                if len(tr)<=5:
                    warn = client.get_channel(notification_channel) 
                    embed = discord.Embed(
                        title=f'The {i[0]} is almost out of stock!' , 
                        description=f"Refill!",
                        colour = discord.Colour.from_rgb(21,82,239))
                    #embed.set_thumbnail(url=welcome_th)
                    embed.add_field(name='Use :', value =f"`shop.comm`", inline = True)
                    embed.set_footer(text =footer )
                    await warn.send(content = None, embed=embed) 
                    with open("products.txt", "r",encoding='utf-8') as f:
                        lines = f.readlines()
                    with open("products.txt", "w",encoding='utf-8') as f:
                        for line in lines:
                            if i[0] not in line.strip("\n"):
                                f.write(line)

async def get_all_transactions():
    account = client2.get_primary_account()
    transactions = client2.get_transactions(account['id']) 
    with open('transactions_record.txt','r+') as tran_rec:
        records = tran_rec.readlines()
        for transaction in transactions['data']:
            time = True
            transaction_gen = (client2.get_transaction(account['id'], transaction['id']))
            try:
                transaction_hash = transaction_gen['network']['hash']
            except:continue
            for record in records:
                if f"{transaction_hash}" in record:
                    time = False
                    break
            if time == False:
                continue
            if transaction['status'] == 'completed':
                print(f'New transaction: {transaction_hash}')
                print('--------------------------------------------------------')
                amount_crypto = f"{transaction_gen['amount']['amount']} {transaction_gen['amount']['currency']}"
                amount_fiat = f"{transaction_gen['native_amount']['amount']} {transaction_gen['native_amount']['currency']}"
                tran_rec.write(f"{transaction_hash}|{transaction['id']}|{amount_crypto}|{amount_fiat}\n")
                not_channel = client.get_channel(notification_channel)
                new = discord.Embed(
                    title=f'New transaction' , 
                    description=f"<@{owner_id}>",
                    colour = discord.Colour.from_rgb(21,82,239))
                new.add_field(name = 'Amount in crypto: ', value =f'`{amount_crypto}`', inline = False)
                new.add_field(name = 'Amount in fiat: ', value =f'`{amount_fiat}`', inline = False)
                new.set_footer(text =f'Thanks for using our services!' )
                await not_channel.send(embed=new,content=None)
        
async def check_transaction_txt():
    new_transactions = []
    with open('transactions_record.txt','r+') as tran_rec,open('checking_list.txt', 'r+') as check_rec:
        confirmed_hashes = tran_rec.readlines()
        client2_hashes = check_rec.readlines()
        for client2_hash in client2_hashes:
            for confirmed_hash in confirmed_hashes:
                if client2_hash.strip().split('|')[0] in confirmed_hash:
                    with open('transactions_record.txt','w') as tran_rec2,open('checking_list.txt', 'w') as check_rec2:
                        confirmed_hashes.remove(confirmed_hash)
                        client2_hashes.remove(client2_hash)
                        new_transactions.append(f"{confirmed_hash.strip()}|{client2_hash.strip().split('|')[1]}")
                        tran_rec2.write(''.join(confirmed_hashes))
                        check_rec2.write(''.join(client2_hashes))
        return new_transactions

async def check_client2_transaction(ctx,hash):
    with open('transactions_record.txt','r+') as tran_rec:
        lines = tran_rec.readlines()
        for transaction in lines:
            if f'{hash}' in transaction:
                with open('transactions_record.txt','r+') as tran_wec:
                    lines.remove(transaction)
                    tran_wec.write(''.join(lines))
                return transaction
        with open('checking_list.txt', 'r+') as check_rec:
            if f'{hash}' not in check_rec.readlines():
                check_rec.write(f'{hash}|{ctx.channel.id}\n')
        return False
   
@client.command()
async def pay(ctx, product_no, quantity):
    await ctx.channel.purge(limit=1)
    quantity = int(quantity)
    product_no = int(product_no)
    token = ctx.channel.id
    print(token)
    with open('products.txt', 'r') as pro:
        prod = pro.readlines()
        get = prod[product_no-1].split('||')[0]

    embed = discord.Embed(
        title=f'Sumarry' , 
        description=f"**You purchased** `{quantity}` - `{get}`",
        colour = discord.Colour.from_rgb(21,82,239))
    with open('products.txt','r', encoding='utf-8') as loops:
        i = 1
        for loop in loops:
                loop = loop.strip()
                loop = loop.split('||')
                if i == int(product_no):
                    amount = loop[1]
                    break
                i+=1
    embed.add_field(name='Amount :', value =f'`{float(amount[:-1])*quantity}{amount[-1]}`', inline = True)
    await ctx.channel.send(embed = embed, content = None)

    embed = discord.Embed(
        title=f'Crypto' , 
        description=f"write command without [ ] to check your transaction\n `cb.crypto [transaction id]`",
        colour = discord.Colour.from_rgb(21,82,239))
    embed.add_field(name='BTC address', value =f'`{btc_add}`', inline = False)
    embed.add_field(name='ETH address', value =f'`{eth_add}`', inline = False)
    await ctx.channel.send(embed = embed, content = None)

    embed = discord.Embed(
        title=f'Paypal' , 
        description=f"Paypal Friend & Family (only)",
        colour = discord.Colour.from_rgb(21,82,239))
    embed.add_field(name='Add a ***NOTE***  to your payment:', value =f"`{token}`", inline = True)
    embed.add_field(name='Paypal email', value =f'`{user_n}`', inline = False)
    embed.add_field(name='IMPORTANT', value =f'Remember to **include a NOTE** in the payment', inline = False)
    embed.add_field(name='For mobile users', value =f'The note has been sent underneath!', inline = False)
    await ctx.channel.send(embed = embed, content = None)
    await ctx.channel.send(token)
    with open('orders.txt','a') as ord:
        ord.write(f'{get}||{quantity}||{token}||{float(amount[:-1])*quantity}{amount[-1]}\n') 

@client.command()
async def crypto(ctx,hash):
    with open('blacklist.txt','r+') as readonly:
        blacklisted = readonly.readlines()
        if f'{hash}\n' in blacklisted:
            negative = discord.Embed(
                title=f'This transaction is blacklisted' , 
                description=f"Please contact Support",
                colour = discord.Colour.from_rgb(21,82,239))
            negative.set_footer(text =f'Thanks for using our services!' )
            await ctx.channel.send(embed = negative, content = None)
            return
        else:
            readonly.write(f'{hash}\n')
    new_transaction = await check_client2_transaction(ctx,hash)
    if new_transaction != False:
        positive = discord.Embed(
            title=f'Transaction confirmed!' , 
            description=f"Owner will appear shortly <@{owner_id}>",
            colour = discord.Colour.from_rgb(21,82,239))
        positive.add_field(name = 'Hash: ', value =f"`{new_transaction.split('|')[0]}`", inline = False)
        positive.add_field(name = 'Amount in crypto: ', value =f"`{new_transaction.split('|')[2]}`", inline = False)
        positive.add_field(name = 'Amount in fiat: ', value =f"`{new_transaction.split('|')[3]}`", inline = False)
        positive.set_footer(text =f'Thanks for using our services!' )
        await ctx.channel.send(embed = positive, content = None)
        with open('orders.txt', 'r')as o_r:
            lines = o_r.readlines()
            for line in lines:
                if str(ctx.channel.id) in line:
                    if int(new_transaction.split('|')[3].split('.')[0]) < int(line.split('||')[-1].strip())- money_check:
                        pr = discord.Embed(
                            title=f'Transaction blocked! Insufficient payment!' , 
                            description=f"Owner will appear shortly <@{owner_id}>",
                            colour = discord.Colour.from_rgb(21,82,239))
                        pr.set_footer(text =f'Thanks for using our services!' )
                        await ctx.channel.send(embed = pr, content = None)
                        continue
                    await send_products(ctx.channel.id,ctx.channel)
    else:
        negative = discord.Embed(
            title=f'Transaction not confirmed!' , 
            description=f"You will be **notified** when it's in our system",
            colour = discord.Colour.from_rgb(21,82,239))
        negative.set_footer(text =f'Thanks for using our services!' )
        await ctx.channel.send(embed = negative, content = None)

@tasks.loop(minutes=5)
async def get_messages():   
    print('executing task')
    await get_all_transactions()
    print('stopped task')


@tasks.loop(minutes=5)
async def sending_messages():
    for new_transaction in await check_transaction_txt():
        customer_channel_id = int(new_transaction.split('|')[-1])
        customer_channel = client.get_channel(int(new_transaction.split('|')[-1]))
        positive = discord.Embed(
            title=f'Transaction confirmed!' , 
            description=f"Owner will appear shortly <@{owner_id}>",
            colour = discord.Colour.from_rgb(21,82,239))
        positive.add_field(name = 'Hash: ', value =f"`{new_transaction.split('|')[0]}`", inline = False)
        positive.add_field(name = 'Amount in crypto: ', value =f"`{new_transaction.split('|')[2]}`", inline = False)
        positive.add_field(name = 'Amount in fiat: ', value =f"`{new_transaction.split('|')[3]}`", inline = False)
        positive.set_footer(text =f'Thanks for using our services!' )
        await customer_channel.send(embed = positive, content = None)
        with open('orders.txt', 'r')as o_r:
            lines = o_r.readlines()
            for line in lines:
                if str(customer_channel_id) in line:
                    print(int(line.split('||')[-1].split('.')[0].strip()), int(line.split('||')[-1].split('.')[0]))
                    if int(new_transaction.split('|')[3].split('.')[0]) < int(line.split('||')[-1].split('.')[0].strip())- money_check:
                        pr = discord.Embed(
                            title=f'Transaction blocked! Insufficient payment!' , 
                            description=f"Owner will appear shortly <@{owner_id}>",
                            colour = discord.Colour.from_rgb(21,82,239))
                        pr.set_footer(text =f'Thanks for using our services!' )
                        await customer_channel.send(embed = pr, content = None)
                        continue
                    await send_products(customer_channel_id,customer_channel)

@tasks.loop(minutes=3)   
async def paypal_check():
    mail = imaplib.IMAP4_SSL(host)
    mail.login(user_n,passw)
    mail.select('inbox')
    current_order = []
    final = []
    m_search, d_search = mail.search(None, 'UNSEEN')
    for item in d_search[0].split():
        current_data = {}
        fill, data = mail.fetch(item,'(RFC822)')
        fill_2, byte = data[0]
        email_msg = email.message_from_bytes(byte)
        for html_header in ['subject','to','from','date']: 
            current_data[html_header] = email_msg[html_header]
        print(current_data['subject'], current_data['from'])
        #if  'paypal@service.com' not in current_data['from'] or 'got' not in current_data['subject'] :
        #    print('conti')
        #    continue
        for spec in email_msg.walk():
            if spec.get_content_type() == "text/plain":
                spec_body = spec.get_payload(decode=True)
                current_data['body'] = spec_body.decode()
            if spec.get_content_type() == "text/html":
                spec_body = spec.get_payload(decode=True)
                current_data['html_body'] = spec_body.decode()
        current_order.append(current_data)
    for order in current_order:
        info = {}
        soup = bs(order['html_body'], 'lxml')
        #print(soup.prettify())
        #print(soup)
        print(order['html_body'])
        #info['note'] = '813839133415178240'
        info['note'] = soup.find('td', style='font-family:Calibri,Trebuchet,Arial,sans serif;font-size:28px;line-height:36px;color:#444444').text
        info['tran_id'] = soup.find('td', style='font-family:Calibri,Trebuchet,Arial,sans serif;font-size:13px;line-height:18px;color:#777777').text.split(':')[1].replace('\xa0', '')
        info['amount'] = soup.find('td', style='font-family:Calibri,Trebuchet,Arial,sans serif;font-size:20px;line-height:22px;color:#333333').text.strip().replace('\xa0', '')
        info['name'] = soup.find('td', style='font-family:Calibri,Trebuchet,Arial,sans serif;font-size:14px;line-height:18px;color:#777777;padding:20px').text.split(',')[1].replace('.','')
        print(info)
        channelpayments = client.get_channel(notification_channel)  
        embed = discord.Embed(
            title=f'New Paypal payment!' , 
            description=f"Payment from {info['name']}",
            colour = discord.Colour.from_rgb(21,82,239))
        #embed.set_thumbnail(url=welcome_th)
        embed.add_field(name='Amount :', value =f"`{info['amount']}`", inline = True)
        try:
            embed.add_field(name='Note :', value =f"`{info['note']}`", inline = True)
        except:
            pass
        embed.add_field(name='Transaction ID :', value =f"`{info['tran_id']}`", inline = True)
        embed.set_footer(text =footer )
        await channelpayments.send(content = None, embed=embed)

        channelapp = client.get_channel(int(info['note']))
        embed = discord.Embed(
            title=f'We have received your payment!' , 
            description=f"Payment from {info['name']}",
            colour = discord.Colour.from_rgb(21,82,239))
        #embed.set_thumbnail(url=welcome_th)
        embed.add_field(name='Owner :', value =f"<@{owner_id}>", inline = True)
        embed.add_field(name='Amount :', value =f"`{info['amount']}`", inline = True)
        embed.add_field(name='Transaction ID :', value =f"`{info['tran_id']}`", inline = True)
        embed.set_footer(text =footer )
        await channelapp.send(content = None, embed=embed)
        channel_id = info['note'].strip()
        with open('orders.txt', 'r')as o_r:
            lines = o_r.readlines()
            for line in lines:
                if str(int(info['note'])) in line:
                    if int(info['amount']) < int(line.split('||')[-1].strip())- money_check:
                        pr = discord.Embed(
                            title=f'Transaction blocked! Insufficient payment!' , 
                            description=f"Owner will appear shortly <@{owner_id}>",
                            colour = discord.Colour.from_rgb(21,82,239))
                        pr.set_footer(text =f'Thanks for using our services!' )
                        await channelapp.send(embed = pr, content = None)
                        continue
                    await send_products(channel_id,channelapp)
        

@client.command()
async def run(ctx):
    await ctx.channel.send('Running')
                    

client.run('')       #token bot
