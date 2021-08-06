from dotenv import load_dotenv
from os import environ
from tweepy import OAuthHandler, API, StreamListener, Stream
from re import sub, findall
from random import choice
from datetime import datetime
from pytz import timezone
from queue import Queue

def load(variables) -> dict:
    """Load environment variables."""
    keys = {}
    load_dotenv() # load .env file
    for var in variables:
        try:
            if var == "VERBOSE": # check is VERBOSE is set
                try:
                    res = bool(environ[var])
                except:
                    res = False # if not its False
            elif var == "WHITELIST": # check if WHITELIST is set
                try:
                    res = list(set(environ[var].split(",")) - {""})
                except:
                    res = [] # if not its an empty list
            else:
                res = environ[var]
            if var == "PSEUDOS":
                res = list(set(res.split(",")) - {""}) # create a list for the channels and remove blank channels and doubles
            keys[var] = res
        except KeyError:
            print(f"Veuillez définir la variable d'environnement {var} (fichier .env supporté)")
            exit(1)
    return keys

def cleanTweet(tweet: str) -> str:
    """Remove all unwanted elements from the tweet."""                    
    tweet =  tweet.lower()                                  # convert to lower case
    tweet = sub(r"(https?:\/\/\S+|www.\S+)", " ", tweet)    # remove URLs
    hashtagMatch = findall(r"#\S+", tweet)      # check all hashtags
    if len(hashtagMatch) < 3:                   # if less than 3
        tweet = sub(r"#\S+", " ", tweet)        # remove them
    else:
        return ""                               # too much hashtags, ignoring tweet
    tweet = sub(r"@\S+", " ", tweet)                        # remove usernames
    tweet = sub(r" *?[^\w\s]+", " ", tweet)                 # remove everything who is not a letter or a number or a space
    tweet = sub(r"\S+(?=si|ci)", " ", tweet)                 # remove element of the word only if the last syllable can be matched (so more words will be answered without adding them manually)
    tweet = sub(r"(?<=ui)i+|(?<=na)a+(?<!n)|(?<=quoi)i+|(?<=no)o+(?<!n)|(?<=hei)i+(?<!n)|(?<=si)i+", "", tweet) # remove key smashing in certains words
    
    return tweet.strip()

class Listener(StreamListener):
    """Watch for tweets that match criteria in real-time."""
    def __init__(self, api = None, users = None, q = Queue()):
        super(Listener, self).__init__()
        self.q = q
        self.api = api
        self.users = users
        self.listOfFriendsID = getFriendsID(api, users)

    def on_connect(self):
        print(f"Scroll sur Twitter avec les abonnements de @{', @'.join(self.users)} comme timeline...")
    
    def on_disconnect(notice):
        notice = notice["disconnect"]
        print(f"Déconnexion (code {notice['code']}).", end = " ")
        if len(notice["reason"]) > 0:
            print(f"Raison : {notice['reason']}")

    def on_status(self, status):
        if status._json["user"]["id"] in self.listOfFriendsID and status._json["user"]["screen_name"] not in keys["WHITELIST"]: # verification of the author of the tweet
            if seniority(status._json["created_at"]): # verification of the age of the tweet
                if not hasattr(status, "retweeted_status"): # ignore Retweet
                    if "extended_tweet" in status._json:
                        tweet = cleanTweet(status.extended_tweet["full_text"])
                    else:
                        tweet = cleanTweet(status.text)
                    lastWord = tweet.split()[-1:][0]
                    if keys["VERBOSE"]:
                        infoLastWord = f"dernier mot : \"{lastWord}\"" if len(lastWord) > 0 else "tweet ignoré car trop de hashtags"
                        print(f"Tweet trouvé de {status._json['user']['screen_name']} ({infoLastWord})...", end = " ")
                    if lastWord in universalBase: # check if the last word found is a supported word
                        answer = None
                        for mot in base.items():
                            if lastWord in mot[1]:
                                if mot[0] == "bon":
                                    if datetime.now().hour in range(7, 17): # between 7am and 5pm
                                        answer = answers[mot[0]][0] # jour
                                    else:
                                        answer = answers[mot[0]][1] # soir
                                else:
                                    answer = answers[mot[0]]
                        if answer == None:
                            if keys["VERBOSE"]:
                                print(f"{errorMessage} Aucune réponse trouvée.")
                        else:
                            if keys["VERBOSE"]:
                                print(f"Envoie d'un {answer[0]}...", end = " ")
                            try: # send answer
                                self.api.update_status(status = choice(answer), in_reply_to_status_id = status._json["id"], auto_populate_reply_metadata = True)
                                print(f"{status._json['user']['screen_name']} s'est fait {answer[0]} !")
                            except Exception as error:
                                if error.message[0]["code"] == 385:
                                    error.message[0]['message'] = "Tweet supprimé ou auteur en privé/bloqué."
                                print(f"{errorMessage[:-2]} ({error[0]['code']}) ! {error[0]['message']}")
                    else:
                        if keys["VERBOSE"]:
                            print("Annulation car le dernier mot n'est pas intéressant.")

    def do_stuff(self):
        while True:
            self.q.get()
            self.q.task_done()

    def on_error(self, status_code):
        print(f"{errorMessage[:-2]} ({status_code}) !", end = " ")
        if status_code == 413:
            if keys["VERBOSE"]:
                print("La liste des mots est trop longue (triggerWords).")
        elif status_code == 420:
            if keys["VERBOSE"]:
                print("Déconnecter du flux.")
        else:
            print("\n")
        return False

def getFriendsID(api, users: list) -> list:
    """Get all friends of choosen users."""
    liste = []
    for user in users:
        liste.extend(api.friends_ids(user))
    return list(set(liste))

def seniority(date: str) -> bool:
    """Return True only if the given string date is less than one day old."""
    datetimeObject = datetime.strptime(date, "%a %b %d %H:%M:%S +0000 %Y") # convert String format to datetime format
    datetimeObject = datetimeObject.replace(tzinfo = timezone("UTC")) # Twitter give us an UTC time
    age = datetime.now(timezone("UTC")) - datetimeObject # time now in UTC minus the time we got to get the age of the date
    return False if age.days >= 1 else True # False if older than a day

def permute(array: list) -> list:
    """Retrieves all possible combinations for the given list and returns the result as a list."""
    quoiListe = []

    for text in array: # all element of the list
        if text.lower() not in quoiListe:
            quoiListe.append(text.lower())      # word fully in lowercase
        if text.upper() not in quoiListe:
            quoiListe.append(text.upper())      # word fully in uppercase
        if text.capitalize() not in quoiListe:
            quoiListe.append(text.capitalize()) # word with the first letter in uppercase
    return quoiListe

def createBaseTrigger(lists) -> list:
    """Merges all given lists into one."""
    listing = []
    for liste in lists:
        listing.extend(liste)
    return list(set(listing))

def createBaseAnswers(word) -> list:
    """Generates default answers for a given word."""
    return [word, f"({word})", word.upper(), f"{word} lol"]

def main(accessToken: str, accessTokenSecret: str, consumerKey: str, consumerSecret: str, users: list):
    """Main method."""
    auth = OAuthHandler(consumerKey, consumerSecret)
    auth.set_access_token(accessToken, accessTokenSecret)
    
    api = API(auth_handler = auth, wait_on_rate_limit = True)

    if keys["VERBOSE"]:
        try:
            api.verify_credentials()
            print(f"Authentification réussie en tant que", end = " ")
        except:
            print("Erreur d'authentification.")
            exit(1)
        print(f"@{api.me()._json['screen_name']}.")
    
    if keys['WHITELIST'] == []:
        whitelist = "Aucun"
    else:
        whitelist = f"@{', @'.join(keys['WHITELIST'])}"
    print(f"Liste des comptes ignorés : {whitelist}.")

    listener = Listener(api, users)
    stream = Stream(auth = api.auth, listener = listener)
    stream.filter(track = triggerWords, languages = ["fr"], stall_warnings = True, is_async = True)

if __name__ == "__main__":
    """
    TOKEN is the Access Token available in the Authentication Tokens section under Access Token and Secret sub-heading.
    TOKEN_SECRET is the Access Token Secret available in the Authentication Tokens section under Access Token and Secret sub-heading.
    CONSUMER_KEY is the API Key available in the Consumer Keys section.
    CONSUMER_SECRET is the API Secret Key available in the Consumer Keys section.
    --
    PSEUDO is the PSEUDO of the account you want to listen to snipe.
    """
    errorMessage = "Une erreur survient !" # error message

    base = { # words to detect in lowercase
        "quoi": ["quoi", "koi", "quoient"],
        "oui": ["oui", "ui", "wi"],
        "non": ["non", "nn"],
        "nan": ["nan"],
        "hein": ["hein", "1"],
        "ci": ["ci", "si"],
        "con": ["con"],
        "ok": ["ok", "okay", "oké", "k"],
        "ouais": ["ouais", "oué"],
        "comment": ["comment"],
        "mais": ["mais", "mé"],
        "fort": ["fort"],
        "coup": ["coup", "cou"],
        "ca": ["ca", "ça", "sa"],
        "bon": ["bon"],
        "qui": ["qui", "ki"]
    }

    answers = { # creation of answers
        "quoi": createBaseAnswers("feur") + [
            "https://twitter.com/Myshawii/status/1423219640025722880/video/1",
            "feur (-isson)",
            "https://twitter.com/Myshawii/status/1423219684552417281/video/1",
            "feur (-issonictalopediatreuil)"
        ],
        "oui": createBaseAnswers("stiti"),
        "non": createBaseAnswers("bril"),
        "nan": createBaseAnswers("cy"),
        "hein": createBaseAnswers("deux") + [
            "2"
        ],
        "ci": createBaseAnswers("tron"),
        "con": createBaseAnswers("combre"),
        "ok": createBaseAnswers("sur glace"),
        "ouais": createBaseAnswers("stern"),
        "comment": createBaseAnswers("tateur"),
        "mais": createBaseAnswers("on"),
        "fort": createBaseAnswers("boyard") + [
            "boyard (-ennes)"
        ],
        "coup": createBaseAnswers("teau"),
        "ca": createBaseAnswers("pristi"),
        "bon": [createBaseAnswers("jour"), createBaseAnswers("soir")],
        "qui": createBaseAnswers("wi") + createBaseAnswers("mono")
    }

    universalBase = createBaseTrigger(list(base.values())) # creation of a list of all the words

    triggerWords = permute(universalBase) # creation of a list of all the words (upper and lower case)

    # loading environment variables and launching the bot
    keys = load(["TOKEN", "TOKEN_SECRET", "CONSUMER_KEY", "CONSUMER_SECRET", "PSEUDOS", "VERBOSE", "WHITELIST"])
    main(keys["TOKEN"], keys["TOKEN_SECRET"], keys["CONSUMER_KEY"], keys["CONSUMER_SECRET"], keys["PSEUDOS"])
