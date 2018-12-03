import datetime
import subprocess
import time
import threading
import csv
import scnsrc
import eserienjunkies
import deleteFilter
import requests
from bs4 import BeautifulSoup
import telepot
import telepot.api
from telepot.loop import MessageLoop
address_pool = []
iniNames = []
module_pool = []
path = "/home/USERNAME/movieupdater/"

for i in range(0,10002):
    iniNames.append(i)

def always_use_new(req, **user_kw):
    return None

telepot.api._which_pool =  always_use_new

def doIt():
    global module_pool
    with open(str(path) + "address_book.csv") as book:
        reader = csv.reader(book, delimiter=",")
        for row in reader:
            address_pool.append(int(str(row[0]).replace('.','')))


    if len(address_pool) > 0:
        bot.sendMessage(address_pool[0], "...restart of bot...")
        print("Address pool:")
        for user in address_pool:
            print(str(user))
    iniNamesCounter = 0
    module_pool.append(eserienjunkies)
    module_pool.append(scnsrc)


    while(True):
        message = " "
        print("update..")

        for module in module_pool:
            print("checking " + str(module.getName()))
            a = getUpdate(iniNamesCounter, module)
            for key in a:
                if key == "iniNamesCounter":
                    iniNamesCounter = int(a.get(key))
                    continue
                print(key)
                message += str(key) + "\n"
                print(a.get(key))
                message += str(a.get(key)) + "\n\n"
            print("\n")
            time.sleep(15)
            if message is not " " and len(address_pool) > 0:
                for user in address_pool:
                    genreList = []
                    with open(str(path) + "genreFilter.csv", "r") as file:
                        reader = csv.DictReader(file)
                        for row in reader:
                            if row['chat_id'] == str(user):
                                genreList.append(row['genre'])
                        if len(genreList) > 0:
                            print("User has an active filter.. ID: " + str(user))
                            messageUser = " "
                            for key in a:
                                if key == "iniNamesCounter":
                                    continue
                                included = False
                                for genre in genreList:
                                    if genre.upper() in key.upper().split(" "):
                                        included = True
                                    if len(genre.split(" ")) > 1:
                                        included = True
                                        for mandatoryGenre in genre.upper().split(" "):
                                            if mandatoryGenre.upper() not in key.upper().split(" "):
                                                included = False
                                    if included:
                                        break
                                if included:
                                    messageUser += str(key) + "\n"
                                    messageUser += str(a.get(key)) + "\n\n"
                                    ########Downloading########
                                    if((user == address_pool[1]) or (user == address_pool[0])):
                                        moduleName = key.split(" ")[len(key.split(" "))-1]
                                        movieName = key.rsplit(' ', 1)[0]
                                        movieName = ".".join(movieName.split(" "))
                                        try:
                                            dshtml = fetchSite(str(a.get(key)))
                                            for module in module_pool:
                                                if(str(moduleName) == str(module.getName())):
                                                    added = module.downloadLink(dshtml, str(movieName))
                                                    if(added):
                                                        bot.sendMessage(user, "Successfull added to JD: "+ str(key))
                                        except:
                                            print("Could not add movie to JD...")
                                            bot.sendMessage(address_pool[0], "Unable to add movie to JD")


                                    ###############################################
                                    included = False
                            if messageUser is not " ":
                                print("sent filtered message to " + str(user) + "\n" + str(messageUser))
                                print()
                                try:
                                    bot.sendMessage(user, messageUser, disable_web_page_preview=True)
                                except:
                                    print("Failed to send filtered message..\n")
                            else:
                                print("no filtered message sent\n")
                        else:
                            print("sent message with all episodes to " + str(user))
                            print()
                            try:
                                bot.sendMessage(user, message, disable_web_page_preview=True)
                            except:
                                print("Failed to send message..\n")
                                bot.sendMessage(user, "I found to many new epsiodes (to big for telegram). Please set personal filters.\n" + str(module.getName()))
            message = " "

        for i in range(0,4):
            time.sleep(300)
            print(".")
        #bot.sendMessage(address_pool[0], "heartbeat..", disable_notification=True)
        #print("heartbeat sent..")

def fetchSite(site):
    try:
        r = requests.get(str(site))
        t = r.text
        html = BeautifulSoup(t, 'html.parser')
        return html
    except:
        print('Could not fetch site')
        bot.sendMessage(address_pool[0], "Could not fetch site: " + str(site))
        return None


def getUpdate(iniNamesCounter, module):
    global iniNames
    html = fetchSite(str(module.getURL()))
    try:
        iniNamesCounter = int(iniNamesCounter)
        iniNamesCounterTemp = iniNamesCounter
        iniNamesTemp = iniNames[:]
        dic = {}
        foundEpisodes = ""
        ###############################
        #print(module.getMovies(html))
        ###############################
        for movie in module.getMovies(html):
            #print(movie)
            movie = movie[0]
            link = movie.get("href")
            ar = movie.text.split(".")
            ar.append(str(module.getName()))
            if " ".join(ar) not in iniNames:
                foundEpisodes += "+"
                iniNames[iniNamesCounter] = " ".join(ar)
                iniNamesCounter += 1
                dic[" ".join(ar)] = link
                if iniNamesCounter >= 10000:
                    iniNamesCounter = 0
                    print("starting puffer from zero")
        if len(dic) == 0:
            print("no new episodes found")
        dic["iniNamesCounter"] = int(iniNamesCounter)
        print(foundEpisodes + "\n[" + str(iniNamesCounter) + "]\n")
        return dic
    except:
        print("Error in getUpdate function! Send empty findings (300s)")
        time.sleep(300)
        iniNamesCounter = iniNamesCounterTemp
        iniNames = iniNamesTemp
        print("Restored old version\n")
        dic = {}
        dic["iniNamesCounter"] = int(iniNamesCounter)
        return dic


def handle(msg):
    global address_pool
    global module_pool
    global path
    chat_id = msg['chat']['id']
    try:
        command = msg['text']
    except:
        print("something other than a string")
        command = "/help"
    print('Got command: ' + str(command) + "\n")

    if command == "/start":
        print("from: " + str(chat_id))
        if chat_id not in address_pool:
            bot.sendMessage(chat_id, """
            Let's go! You're receiving updates now.\n
            /help for help\n
            /thanks to say thank you to the developer""")
            address_pool.append(chat_id)
            print("New address pool:")
            for user in address_pool:
                print(str(user))
            with open(str(path) + "address_book.csv","a", newline='') as book:
                writer = csv.writer(book, delimiter=".")
                writer.writerow(str(chat_id))
        else:
            print("User already in pool..")
        print()
    elif command == "/stop":
        print("from: " + str(chat_id))
        bot.sendMessage(chat_id, "You won't receive further notifications")
        address_pool_temp = address_pool[:]
        address_pool = []
        with open(str(path) + "address_book.csv" ,"w", newline="") as book:
            writer = csv.writer(book, delimiter=".")
            print("New address book:")
            for user in address_pool_temp:
                if user == chat_id:
                    continue
                address_pool.append(user)
                writer.writerow(str(user))
                print(str(user))
            print("\nNew address pool:")
            for user in address_pool:
                print(str(user))
            print()
    elif command == "/filter":
        print("from: " + str(chat_id))
        genreList = []
        with open(str(path) + "genreFilter.csv", "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['chat_id'] == str(chat_id):
                    genreList.append(row['genre'])
        if len(genreList) > 0:
            bot.sendMessage(chat_id, "Here are your activated filters:")
            filterMessage = " "
            filter_count = 0
            for genre in genreList:
                filterMessage += (str(genre) + "\n")
                filter_count += 1
                if filter_count is 50:
                    try:
                        bot.sendMessage(chat_id, filterMessage)
                        print("sent parted filters to user.." + str(chat_id) + "\n")
                        filter_count = 0
                        filterMessage = ""
                    except:
                        print("Failed to sent filter to user.." + str(chat_id) + "\n")
            try:
                bot.sendMessage(chat_id, filterMessage)
                print("sent filters to user.." + str(chat_id)  + "\n")
            except:
                print("Failed to sent filter to user " + str(chat_id) + " \n")
        else:
            bot.sendMessage(chat_id, "Sorry, I cannot find any filters of you :(")
            print("No filters found..\n")
    elif command == "/help":
        print("from: " + str(chat_id))
        helpMail = """/start to start your subscription.
/stop to stop your subscription.
/module to list all activated modules.
/filter for a listing of your filters.
For setting a new filter,
send a single keyword or
multiple words (mandatory filter) in
this chat.
/del FILTERNAME to delete the specific filter.
\n\n
Have fun!"""
        bot.sendMessage(chat_id, helpMail)
    elif command == "/thanks":
        thanksMessage = str(chat_id) + " says thank you for this bot."
        bot.sendMessage(address_pool[0], thanksMessage)
        bot.sendMessage(chat_id, "You made the developer very happy! Enjoy it!")
        print(thanksMessage + "\n")
    elif command.split(" ")[0] == "/del":
        print("from: " + str(chat_id))
        to_delete = command[5:]
        del_stat = deleteFilter.del_f(path, str(chat_id), str(to_delete))
        if del_stat:
            del_message = str(to_delete) + " is deleted. /filter to see your active filters."
            bot.sendMessage(chat_id, del_message)
        else:
            bot.sendMessage(chat_id, "Didn't find a active filter named like: " + str(to_delete))
    elif command == "/module":
        print("from: " + str(chat_id))
        moduleMessage = ""
        for module in module_pool:
            moduleMessage += str(module.getName()) + ": " + str(module.getURL()) + "\n"
        bot.sendMessage(chat_id, moduleMessage, disable_web_page_preview=True)
        print(moduleMessage + "\n")
    elif command.split(" ")[0] == "/broadcast":
        if(chat_id == address_pool[0]):
            bcmessage = command[11:]
            for user in address_pool:
                bot.sendMessage(user, bcmessage)
                print("Admin sent message (" + str(bcmessage) + ") to " + str(user))

            print("\n")
        else:
            print("Random user tried to sent broadcast message!!! " + str(chat_id) + "\n")
    else:
        bot.sendMessage(chat_id, "New filter for you: " + str(command))
        with open(str(path) + 'genreFilter.csv', 'a') as csvfile:
            fieldnames = ['chat_id', 'genre']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow({'chat_id' : str(chat_id), 'genre' : str(command)})
            print(str(command) + " added to filter for ID: " + str(chat_id) + "\n")


def run():
    doIt()
    time.sleep(1)

# please enter telegram token
bot = telepot.Bot('####################################')

MessageLoop(bot, handle).run_as_thread()

thread = threading.Thread(target=run, args=())
thread.daemon = True                            
thread.start()


print("started...")

while(True):
    time.sleep(10)
