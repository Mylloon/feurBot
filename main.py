from dotenv import load_dotenv
from os import environ
from tweepy import OAuthHandler, API, StreamListener, Stream
from re import sub
from random import choice
from datetime import datetime
from pytz import timezone

def load(variables):
    """Load env variables."""
    keys = {}
    load_dotenv() # load .env file
    for var in variables:
        try:
            res = environ[var]
            if var == "PSEUDOS":
                res = list(set(res.split(',')) - {""}) # create a list for the channels and remove blank channels and doubles
            keys[var] = res
        except KeyError:
            print(f"Please set the environment variable {var} (.env file supported)")
            exit(1)
    return keys

class Listener(StreamListener):
    def __init__(self, api = None, users = None):
        super(Listener, self).__init__()
        self.api = api
        self.listOfFriendsID = getFriendsID(api, users)

    def on_status(self, status):
        """Answer to tweets."""
        if seniority(status._json["created_at"]):
            tweetText = sub(r'https?:\/\/\S+| +?\?|\?| +?\!| ?\!|-|~', '', status._json["text"])
            if tweetText.endswith(tuple(triggerWords)):
                if status._json["user"]["id"] in self.listOfFriendsID:
                    try:
                        self.api.update_status(status = choice(feur), in_reply_to_status_id = status._json["id"], auto_populate_reply_metadata = True)
                        print(f"{status._json['user']['screen_name']} est passé au coiffeur !")
                    except Exception as error:
                        print(f"Error happens! {error}")
                        pass

def getFriendsID(api, users: list):
    liste = []
    for user in users:
        liste.extend(api.friends_ids(user))
    return list(set(liste))

def seniority(date: str):
    datetimeObject = datetime.strptime(date, '%a %b %d %H:%M:%S +0000 %Y') # Convert String format to datetime format
    datetimeObject = datetimeObject.replace(tzinfo = timezone('UTC')) # Twitter give us an UTC time
    age = datetime.now(timezone('UTC')) - datetimeObject # Time now in UTC minus the time we got to get the age of the date
    return False if age.days >= 1 else True # False if older than a day

def permute(array: list):
    quoiListe = []

    for text in array: # all element of the list
        n = len(text)
        mx = 1 << n # Number of permutations is 2^n
        text = text.lower() # Converting string to lower case

        for i in range(mx): # Using all subsequences and permuting them
            combination = [k for k in text]
            for j in range(n):
                if (((i >> j) & 1) == 1): # If j-th bit is set, we convert it to upper case
                    combination[j] = text[j].upper()

            temp = ""
            for i in combination:
                temp += i
            quoiListe.append(temp)
    return quoiListe

def main(accessToken: str, accessTokenSecret: str, consumerKey: str, consumerSecret: str, users: list):
    """Main method."""
    auth = OAuthHandler(consumerKey, consumerSecret)
    auth.set_access_token(accessToken, accessTokenSecret)
    
    api = API(auth_handler = auth, wait_on_rate_limit = True)

    listener = Listener(api, users)
    stream = Stream(auth = api.auth, listener = listener)

    print(f"Scroll sur Twitter avec les abonnements de @{', @'.join(users)}...")
    stream.filter(track = triggerWords, languages = ["fr"], is_async = True)

if __name__ == '__main__':
    """
    TOKEN is the Access Token available in the Authentication Tokens section under Access Token and Secret sub-heading.
    TOKEN_SECRET is the Access Token Secret available in the Authentication Tokens section under Access Token and Secret sub-heading.
    CONSUMER_KEY is the API Key available in the Consumer Keys section.
    CONSUMER_SECRET is the API Secret Key available in the Consumer Keys section.
    --
    PSEUDO is the PSEUDO of the account you want to listen to snipe.
    """
    quoiBase = ["quoi", "koi"]
    triggerWords = permute(quoiBase)
    feur = ["feur", "(feur)", "FEUR", "feur lol", "https://twitter.com/shukuzi62/status/1422611919538724868/video/1"]
    keys = load(["TOKEN", "TOKEN_SECRET", "CONSUMER_KEY", "CONSUMER_SECRET", "PSEUDOS"])
    main(keys["TOKEN"], keys["TOKEN_SECRET"], keys["CONSUMER_KEY"], keys["CONSUMER_SECRET"], keys["PSEUDOS"])
