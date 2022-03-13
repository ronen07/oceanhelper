import datetime
import hashlib
import json
import os
import platform
import random
import threading
import time
import traceback
from asyncio import sleep
import logging
import sys
import discord
import requests

from bs4 import BeautifulSoup as bs
from discord.ext import commands
from multiprocessing.connection import Client, Listener

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

botdata = {}
ports = [1026]
HOST_PORT = 1025
authkey = b"authkey"


class Config:
    def __init__(self, client):
        self.bot = client

    def listener(self, port: int) -> Listener:
        global ports

        assert port not in ports if not port == 1026 else True
        ports.append(port)

        print(f"Opening listener on port {port}")
        return Listener(("localhost", port), authkey=authkey)

    def host(self):
        listener = Listener(("localhost", HOST_PORT), authkey=authkey)

        while True:
            try:
                conn = listener.accept()
                data = conn.recv()

                if data == "close":
                    for port in ports:
                        print(f"Sending command on port {port}")
                        client = Client(("localhost", port), authkey=authkey)
                        client.send(data)

                    listener.close()
                    break

                for port in ports:
                    client = Client(("localhost", port), authkey=authkey)
                    client.send(data)

                DataIO(self.bot).savetofile(data)
            except:
                print("Caught exception!")
                traceback.print_exc()

class DataIO:

    def __init__(self, bot):
        self.bot = bot

    def getdata(self):
        slapgifs = []
        fightgifs = []
        facts = []

        bannedlinks = ["https://media.tenor.com/images/9865eae3e8f2db81f0aab6a37febd1ce/tenor.gif",
                       "https://media.tenor.com/images/91b5cd8aa518c4b88c96f05e79749d0c/tenor.gif",
                       "https://media.tenor.com/images/7766f3d163f651b6d9d7c3b718d8e6fb/tenor.gif",
                       "https://media.tenor.com/images/9865eae3e8f2db81f0aab6a37febd1ce/tenor.gif",
                       "https://media.tenor.com/images/ac3179252c6ca6aa2883dfff91820421/tenor.gif",
                       "https://media.tenor.com/images/9865eae3e8f2db81f0aab6a37febd1ce/tenor.gif",
                       "https://media.tenor.com/images/0cb904d17951de0e16ffd15ef5d2996b/tenor.gif",
                       "https://media.tenor.com/images/0cb904d17951de0e16ffd15ef5d2996b/tenor.gif",
                       "https://media.tenor.com/images/bcd979fe49f1e7c99baf05abedc00ebb/tenor.gif",
                       "https://media.tenor.com/images/29aaa973f0500947b7bda6b14e4a253f/tenor.gif",
                       "https://media.tenor.com/images/3bada7baa65871e56c2bac1a584075c5/tenor.gif",
                       "https://media.tenor.com/images/da85643ae6efc6e8af21abb7f26cca32/tenor.gif",
                       "https://media.tenor.com/images/d1e4abc20a778e1e11b1363621012078/tenor.gif",
                       "https://media.tenor.com/images/ffe8587e302d7ed5b82196d89f2c1b94/tenor.gif",
                       "https://media.tenor.com/images/f775a57b776b455985139447b9411644/tenor.gif",
                       "https://media.tenor.com/images/9dec8b11cb3557fbb073f93ee7d03be5/tenor.gif",
                       "https://media.tenor.com/images/da85643ae6efc6e8af21abb7f26cca32/tenor.gif",
                       "https://media.tenor.com/images/9dec8b11cb3557fbb073f93ee7d03be5/tenor.gif",
                       "https://media.tenor.com/images/f775a57b776b455985139447b9411644/tenor.gif",
                       "https://media.tenor.com/images/d1e4abc20a778e1e11b1363621012078/tenor.gif",
                       "https://media.tenor.com/images/ffe8587e302d7ed5b82196d89f2c1b94/tenor.gif",
                       "https://media.tenor.com/images/e4d9dfda188b8ee012f4b0ac12aa9c08/tenor.gif",
                       "https://media.tenor.com/images/2b983ab0ddc99168b33e18fd1c9b200f/tenor.gif",
                       "https://media.tenor.com/images/ce0c15bf4531541b9dc836ec90c826ce/tenor.gif",
                       "https://media.tenor.com/images/b40a77e274850a9d68831d89dd76b678/tenor.gif",
                       "https://media.tenor.com/images/47698b115e4185036e95111f81baab45/tenor.gif",
                       "https://media.tenor.com/images/a0c111e14b73a5ff9a876eb6beab6729/tenor.gif",
                       "https://media.tenor.com/images/9d58468e90e30280c3d7e23eebc9fdb8/tenor.gif",
                       "https://media.tenor.com/images/65cb561328eddb5d6c567e66a02c5d21/tenor.gif",
                       "https://media.tenor.com/images/8d75b4dc8abf24727adc720ff814775f/tenor.gif",
                       "https://media.tenor.com/images/139aab44e862b4b2dc2da85df1ae38cc/tenor.gif",
                       "https://media.tenor.com/images/00dcee3a55b6cfe9c74e47d00954429d/tenor.gif",
                       "https://media.tenor.com/images/e8189a04ebe8b64f616442e650355faa/tenor.gif",
                       "https://c.tenor.com/u-yKuh6zk3UAAAAM/anime-fight.gif",
                       "https://c.tenor.com/uIR76eoQmZgAAAAj/akuma-street-fighter.gif",
                       "https://c.tenor.com/54UvYpH15UQAAAAj/fight-wrestling-match.gif",
                       "https://c.tenor.com/yAvKjzxBGeoAAAAj/snowball-fight.gif",
                       "https://c.tenor.com/3fEndZQZu1kAAAAj/fight-me.gif",
                       "https://c.tenor.com/CVCcyFkv72wAAAAj/goku-vs-frieza-fight.gif",
                       "https://c.tenor.com/pt_Bk5Oo9m0AAAAj/jojo-dio.gif",
                       "https://c.tenor.com/mA8sf-yC61sAAAAj/fight-me.gif",
                       "https://c.tenor.com/PMCDFLsJodEAAAAM/fight-fighting.gif",
                       "https://c.tenor.com/Lkyf9b8203YAAAAM/dragon-maid-kanna-fite.gif"
                       "https://c.tenor.com/FT_O1Qt-SUEAAAAM/zenitsu-fight-zenitsu.gif",
                       "https://c.tenor.com/HCZtYeG_lr8AAAAM/anime-fight.gif",
                       "https://c.tenor.com/tWoLRu4geQEAAAAM/hunter-x-hunter-anime.gif",
                       "https://c.tenor.com/5Ry4AVOgod4AAAAM/bear-fight.gif",
                       "https://c.tenor.com/MPPHbillO_0AAAAM/naruto-fight.gif",
                       "https://c.tenor.com/bRTx1rv16w4AAAAM/anime-bleh.gif",
                       "https://c.tenor.com/i2Q6ReOAR4UAAAAM/rage-anime.gif",
                       "https://c.tenor.com/xgifnu5ewPAAAAAM/anime-fight.gif",
                       "https://c.tenor.com/Lkyf9b8203YAAAAM/dragon-maid-kanna-fite.gif"]

        data = bs(requests.get("https://tenor.com/search/anime-slap-gifs").text, features="html.parser")
        all_gifs = data.select('img')

        for link in all_gifs:
            if "slap" in str(link).lower() and not "spank" in str(link).lower():
                links = str(link).split('"')
                for link in links:
                    if link.endswith(".gif") and not link in bannedlinks:
                        slapgifs.append(link)

        data = bs(requests.get("https://tenor.com/search/fight-anime-gifs").text, features="html.parser")
        all_gifs = data.select('img')

        for link in all_gifs:
            if "fight" in str(link).lower() and not "nipple" in str(link) and not "sex" in str(
                    link) and not "bra" in str(link):
                links = str(link).split('"')
                for link in links:
                    if link.endswith(".gif") and not link in bannedlinks:
                        fightgifs.append(link)

        resp = bs(requests.get("https://www.thefactsite.com/100-space-facts/").text, features="html.parser")
        raw_facts = resp.select("h2")

        for fact in raw_facts:
            if "list" in str(fact):
                fact = str(fact).replace("<h2 class=\"list\">", "")
                fact = fact.replace("</h2>", "")
                fact = fact.replace("<em>", " ")
                fact = fact.replace("</em>", " ")
                facts.append(fact)

        if platform.system().lower() == "darwin":
            nasalinks = json.load(open("/Users/admin/Dundertale/DundertaleBot/data/nasalinks.json", "r"))
        elif platform.system() == "Linux":
            nasalinks = json.load(open("data/nasalinks.json", "r"))
        else:
            raise OSError

        return slapgifs, fightgifs, facts, nasalinks

    def spacex_data(self):
        spacex = {}
        nasa_key = "6FIv9HusPGaDbSZBkONl2W0JRx6C0TSYPFqjCbdR"

        '''while psutil.pid_exists(pid):
            try:
        date = datetime.datetime.now().strftime(r"%m/%d/%Y %H:%M:%S")
        botdata["log"].append(f"{date} refreshing SpaceX data...")'''

        apod = json.loads(requests.get(f"https://api.nasa.gov/planetary/apod?api_key={nasa_key}").text)
        spacex["company"] = json.loads(requests.get("https://api.spacexdata.com/v4/company").text)
        time.sleep(0.5)
        spacex["cores"] = json.loads(requests.get("https://api.spacexdata.com/v4/cores").text)
        time.sleep(0.5)
        spacex["capsules"] = json.loads(requests.get("https://api.spacexdata.com/v4/capsules").text)
        time.sleep(0.5)
        spacex["dragons"] = json.loads(requests.get("https://api.spacexdata.com/v4/dragons").text)
        time.sleep(0.5)
        spacex["history"] = json.loads(requests.get("https://api.spacexdata.com/v4/history").text)
        time.sleep(0.5)
        spacex["starlink"] = json.loads(requests.get("https://api.spacexdata.com/v4/starlink").text)
        time.sleep(0.5)
        spacex["next"] = json.loads(requests.get("https://api.spacexdata.com/v4/launches/next").text)
        spacex["last_updated"] = datetime.datetime.utcnow().strftime(r"%m/%d/%Y %H:%M:%S")

        return apod, spacex

    def gethash(self, value) -> str:
        return hashlib.sha256(value).hexdigest()

    def createconfig(self, scope) -> dict:
        global botdata

        if scope == "server" and id is not None:
            guilddata = {"config": {}}

            guilddata["config"]["someoneping"] = True
            guilddata["config"]["botenabled"] = True
            guilddata["config"]["greetings"] = True
            guilddata["config"]["filterprofanity"] = False
            guilddata["config"]["deleteprofanity"] = False
            guilddata["config"]["noafkchannels"] = []
            guilddata["config"]["modmailchannel"] = []
            guilddata["config"]["antiraid"] = {}
            guilddata["config"]["antiraid"]["enabled"] = False
            guilddata["config"]["antiraid"]["mode"] = "passive"
            guilddata["config"]["antiraid"]["rate"] = [2, 4]
            guilddata["config"]["antiraid"]["log"] = []
            guilddata["config"]["antiraid"]["underraid"] = False
            guilddata["config"]["antiraid"]["banprofanenicks"] = False
            guilddata["config"]["antiraid"]["blacklist"] = []
            guilddata["config"]["antiraid"]["count"] = 0
            guilddata["config"]["antiraid"]["action"] = "kick"
            guilddata["config"]["antiraid"]["revokeinvites"] = False
            guilddata["config"]["antiraid"]["raiseverification"] = False

            guilddata["bulletins"] = {}
            guilddata["bulletins"]["to-do"] = {}
            guilddata["bulletins"]["events"] = {}

            return guilddata

        elif scope == "other":
            botdata["modmailexempt"] = []
            botdata["global"] = {}
            globalconfig = botdata["global"]

            globalconfig["botenabled"] = True
            globalconfig["someoneping"] = True
            globalconfig["greetings"] = True

            botdata["errors"] = []
            botdata["commandscount"] = 0
            botdata["log"] = []
            botdata["blacklist"] = []
            botdata["violations"] = {}
            botdata["warnings"] = {}
            botdata["ratings"] = {}
            botdata["slapcount"] = {}
            botdata["fightcount"] = {}
            botdata["afkmembers"] = {}
            botdata["spacexnotification"] = []
            botdata["pingcooldown"] = []

            return botdata

        raise TypeError("Invalid parameters")

    def loadconfig(self) -> dict:
        if platform.system().lower() == "darwin":
            if os.path.exists("/Users/admin/Dundertale/DundertaleBot/data/botdata.json"):
                botdata = json.load(open("/Users/admin/Dundertale/DundertaleBot/data/botdata.json", "r"))

                return botdata
            else:
                raise FileNotFoundError

        elif platform.system() == "Linux":
            if os.path.exists("data/botdata.json"):
                botdata = json.load(open("data/botdata.json", "r"))

                return botdata
            else:
                raise FileNotFoundError

    def savetofile(self, botdata) -> None:
        print(platform.system())  # do this so you can see what platform.system() is on AWS
        if platform.system().lower() == "darwin":
            json.dump(botdata, open("/Users/admin/Dundertale/DundertaleBot/data/botdata.json", "w"))
        elif platform.system() == "Linux":
            json.dump(botdata, open("data/botdata.json", "w"))
        else:
            raise FileNotFoundError

    def saveconfig(self, botdata):
        client = Client(("localhost", HOST_PORT), authkey=authkey)

        client.send(botdata)
        client.close()

    def getid(self) -> str:
        id = ""
        charlist = list("QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm1234567890")

        for i in range(6):
            id += charlist[random.randint(random.randint(0, len(charlist) - 1), len(charlist))]

        return id

def syncdata(bot):
    global botdata

    listener = Config(bot).listener(port=6969)

    while True:
        try:
            conn = listener.accept()
            data = conn.recv()

            if data == "close":
                listener.close()
                break

            botdata = data
        except Exception as error:
            print(error)


def setup(bot: commands.Bot):
    global botdata

    threading.Thread(target=Config(bot).host).start()
    bot.add_cog(events(bot))
    botdata = DataIO(bot).loadconfig()
    threading.Thread(target=syncdata, args=(bot,)).start()