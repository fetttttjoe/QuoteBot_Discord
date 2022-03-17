# bot.py
#from asyncio.windows_events import NULL
import os
import random
import datetime
import hashlib
import sqlite3
import discord
from discord.embeds import Embed 
from discord.ext import commands
#Bot Token
TOKEN="YOUR TOKEN GOES HERE"

#check if database is made and load it
db = sqlite3.connect('quotes.db')
cursor = db.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS quotes(hash TEXT primary key, server INT, user TEXT, message TEXT, date_added TEXT)')
print("Loaded database")

db.commit()

def beautyOutput(input):
    output=str(input)
    
    output=output.replace(","," ")
    output=output.replace("\""," ")
    output=output.replace("(","")
    output=output.replace(")","")
    output=output.replace("[","")
    output=output.replace("]","")
    
    return output

bot = commands.Bot(command_prefix='!',help_command=None)
@bot.command(name="getallquotes")
async def quoteall(ctx,message:str):

    #get discord id
    serverID = ctx.message.guild.id

    #sanitise name
    user = message
    embedVar= discord.Embed(title="all Quotes")

    sql="SELECT server,message,date_added,user FROM quotes WHERE user=? AND server=?"
    cursor.execute(sql,(user,serverID))
    result=cursor.fetchall()
    print(result)
    if len(result) == 0:
        await ctx.send(f"No Quotes for user in database")
        return
    #CANT remove element from tuple, so convert it into list
    resultList=list(result)
    print(resultList[0])
    print(resultList)
    #adds quotes to message
    for count, item in enumerate(resultList, start=1):

        #print(item)
        #convert list element into string to split it up
        temp = str(item)
        temp=temp.split()
        #remove unnecessary elements in string 
        temp[0]=temp[0].replace("(","")
        temp[0]=temp[0].replace(",","")

        del temp[0]
        temp=" ".join(temp)
        output=beautyOutput(temp)
        embedVar.add_field(name=f"Quote {count}",value=output,inline=False)
    await ctx.send(embed=embedVar)
   
          

    
#help menu
@bot.command(name="help")
async def quotehelp(cxt):
    embedVar = discord.Embed(title="Quotebot commands:", description="Help", color=0x00ff00)
    
    embedVar.add_field(name="To quote:", value="!quote @[user] [message]", inline=False)
    embedVar.add_field(name="To display", value="!getquote @[user]", inline=False)
    embedVar.add_field(name="To display all", value="!getallquotes @[user]", inline=False)
    embedVar.add_field(name="Random quote from a random user", value="!random", inline=False)
    embedVar.add_field(name="Delete quote:", value="!deletequote [message]", inline=False)
    await cxt.send(embed=embedVar)

    

#get quote from specific user
@bot.command(name="getquote")
async def getquote(ctx,message: str):
    
    #get discord id
    serverID = ctx.message.guild.id

    #sanitise name
    user = message
    print("user",user)
    try:
        print(serverID)
        #query random quote from user
        sql="SELECT server,message,date_added FROM quotes WHERE user=? AND server=? ORDER BY RANDOM() LIMIT 1"
        
        cursor.execute(sql,(user,serverID))
        query = cursor.fetchone()

        #adds quotes to message
        #output = "\""+str(query[0])+"\""
        print(query[0])
        if serverID == query[0]:

            output=beautyOutput(query[1])
            #log
            print(message+": \""+output+"\" printed to the screen "+str(query[1]))
            #embeds the output to make it pretty
            style = discord.Embed(name="responding quote", description=message+" "+str(query[2]))
            style.set_author(name=f"\"{output}\"")
            await ctx.send(embed=style)
        
            
    except Exception as exeption:
        print(exeption)
        await ctx.send("No quotes of that user found in database")
#print random quote
@bot.command(name="random")
async def quoterandom(ctx):

    #get discord id
    serverID = ctx.message.guild.id

    sql="SELECT server,user,message,date_added FROM quotes WHERE server=(?) ORDER BY RANDOM() LIMIT 1"
    cursor.execute(sql,[serverID])
    query = cursor.fetchone()
    #print(query)
    
    
    try:
        #embeds the output
        response = discord.Embed(name="responding quote", description="- "+str(query[1])+" "+str(query[3]))
        response.set_author(name=str(query[2]))
        #log
        print(query[1]+": \""+query[2]+"\" printed to the screen added"+str(query[3]))
        await ctx.send(embed=response)
    except Exception:
        response = discord.Embed(Title="Error",description="No Quotes saved yet!!")
        await ctx.send(embed=response)

#del quote
@bot.command(name="deletequote")
async def delquote(ctx,*,message:str):
    string = str(message)
    temp = string.split()
    #get discord id
    serverID = ctx.message.guild.id
    
    
    temp= " ".join(temp)
    print(f"temp: {temp} server id {serverID}")
    try:
        #cursor.execute("SELECT FROM quotes WHERE message=? AND server=?",[temp],[serverID])
        #test=cursor.fetchall
        #print("test",test)
        sql="DELETE FROM quotes WHERE message=? AND server=?"
        cursor.execute(sql,(temp,serverID))
        
        if cursor is None:
            return
        db.commit()
        print(cursor.rowcount, "record(s) deleted") 
        output=beautyOutput(temp)
        await ctx.send(f"deleted {output}")
    except Exception as exeption:
        print(exeption)
        await ctx.send(f"Quote {temp} doesnt exist")


#add quote
@bot.command(name="quote")
async def quote(ctx,*, message: str):
    #get discord id
    serverID = ctx.message.guild.id
    #split the message into words
    string = str(message)
    temp = string.split()

    #take the username out
    user = temp[0]
    del temp[0]

    #join the message back together
    quote = " ".join(temp)
    
    if user[1]!='@':
        await ctx.send("Use ```@[user] [message]``` to quote a person")
        return

    uniqueID = hash(user+message)

    #date and time of the message
    time = datetime.datetime.now()
    formatted_time = str(time.strftime("%d-%m-%Y %H:%M"))
    print(quote)
    #find if message is in the db already
    cursor.execute("SELECT count(*) FROM quotes WHERE hash = ?",(uniqueID,))
    find = cursor.fetchone()[0]

    if find != 0:
        return

    #insert into database
    cursor.execute("INSERT INTO quotes VALUES(?,?,?,?,?)",(uniqueID,serverID,user,quote,formatted_time))
    await ctx.send("Quote successfully added")

    db.commit()

    #number of words in the database
    rows = cursor.execute("SELECT * from quotes")

    #log to terminal
    print(str(len(rows.fetchall()))+". added - "+str(user)+": \""+str(quote)+"\" to database at "+formatted_time)


bot.run(TOKEN)
