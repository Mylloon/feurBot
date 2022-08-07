from dotenv import load_dotenv
from os import environ
from tweepy import StreamingClient, Client, StreamRule
from re import sub, findall
from random import choice
from datetime import datetime
from pytz import timezone
from queue import Queue
from json import loads

def load(variables) -> dict:
    """Load environment variables"""
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
            elif var == "FORCELIST": # check if FORCELIST is set
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
    """Remove all unwanted elements from the tweet"""
    # Convert to lower case
    tweet =  tweet.lower()
    # Remove URLs
    tweet = sub(r"(https?:\/\/\S+|www.\S+)", " ", tweet)
    # Check all hashtags
    hashtagMatch = findall(r"#\S+", tweet)
    # If less than 3
    if len(hashtagMatch) < 3:
        # Remove them
        tweet = sub(r"#\S+", " ", tweet)
    else:
        # Too much hashtags in the tweet -> so ignore it
        return ""
    # Remove usernames
    tweet = sub(r"@\S+", " ", tweet)
    # Remove everything who isn't a letter/number/space
    tweet = sub(r" *?[^\w\s]+", " ", tweet)
    # Remove element of the word only if the last syllable can be matched
    # (so more words will be answered without adding them manually)
    tweet = sub(r"\S+(?=si|ci)", " ", tweet)

    # Remove key smashing in certains words
    #              uiii      naaaan          quoiiii     noooon          heiiin           siiii
    tweet = sub(r"(?<=ui)i+|(?<=na)a+(?<!n)|(?<=quoi)i+|(?<=no)o+(?<!n)|(?<=hei)i+(?<!n)|(?<=si)i+", "", tweet)

    return tweet.strip()

class Listener(StreamingClient):
    """Watch for tweets that match criteria in real-time"""
    def __init__(
        self,
        bearer_token,
        client: Client,
        users: list = [],
        forcelist: list = [],
        q = Queue()
    ):
        super(Listener, self).__init__(bearer_token)
        self.q = q
        self.client = client
        self.accounts = {
            "users": users,
            "forcelist": forcelist
        }
        self.victim_list = getFriends(client, users) + getIDs(client, forcelist)

    def on_connect(self):
        if self.accounts['forcelist'] == []:
            forcelist = "Aucun"
        else:
            forcelist = f"@{', @'.join(self.accounts['forcelist'])}"
        print(f"Début du scroll sur Twitter avec les abonnements de @{', @'.join(self.accounts['users'])} et ces comptes en plus : {forcelist} comme timeline...")

    def on_disconnect_message(notice):
        notice = notice["disconnect"]
        print(f"Déconnexion (code {notice['code']}).", end = " ")
        if len(notice["reason"]) > 0:
            print(f"Raison : {notice['reason']}")

    def on_status(self, status):
        print(status)
        exit(0)
        json = status._json
        # Verify the author of the tweet
        if json["user"]["id"] in self.victim_list and json["user"]["screen_name"] not in keys["WHITELIST"]:
            # Verify the age of the tweet
            if seniority(json["created_at"]):
                # Verify if the tweet isn't a retweet
                if not hasattr(status, "retweeted_status"):
                    # Fetch the tweet
                    if "extended_tweet" in json:
                        tweet = cleanTweet(status.extended_tweet["full_text"])
                    else:
                        tweet = cleanTweet(status.text)
                    # Fetch the last word of the tweet
                    lastWord = tweet.split()[-1:][0]
                    if keys["VERBOSE"]:
                        infoLastWord = f"dernier mot : \"{lastWord}\"" if len(lastWord) > 0 else "tweet ignoré car trop de hashtags"
                        print(f"Tweet trouvé de {json['user']['screen_name']} ({infoLastWord})...", end = " ")
                    # Check if the last word found is a supported word
                    if lastWord in universalBase:
                        answer = None

                        # Check repetition
                        repetition = findall(r"di(\S+)", lastWord)
                        if(len(repetition) > 0):
                            # We need to repeat something...
                            answer = repeater(repetition[0])

                        # Fetch an other adequate (better) response
                        for mot in base.items():
                            if lastWord in mot[1]:
                                # Handle specific case
                                if mot[0] == "bon":
                                    # Between 7am and 5pm
                                    if datetime.now().hour in range(7, 17):
                                        answer = answers[mot[0]][0] # jour
                                    else:
                                        answer = answers[mot[0]][1] # soir
                                else:
                                    # Normal answer
                                    answer = answers[mot[0]]
                        if answer == None:
                            if keys["VERBOSE"]:
                                print(f"{errorMessage} Aucune réponse trouvée.")
                        # If an answer has been found
                        else:
                            if keys["VERBOSE"]:
                                print(f"Envoie d'un {answer[0]}...", end = " ")
                            try:
                                # Send the tweet with the answer
                                # TODO: Update Twitter API V2
                                self.api.update_status(status = choice(answer), in_reply_to_status_id = json["id"], auto_populate_reply_metadata = True)
                                print(f"{json['user']['screen_name']} s'est fait {answer[0]} !")
                            except Exception as error:
                                error = loads(error.response.text)["errors"][0]
                                # https://developer.twitter.com/en/support/twitter-api/error-troubleshooting
                                show_error = True
                                if error["code"] == 385:
                                    error["message"] = f"Tweet supprimé ou auteur ({json['user']['screen_name']}) en privé/bloqué."
                                    show_error = False

                                # Show error only if relevant, always in verbose
                                if show_error or keys["VERBOSE"]:
                                    print(f"{errorMessage[:-2]} ({error['code']}) ! {error['message']}")
                    else:
                        if keys["VERBOSE"]:
                            print("Annulation car le dernier mot n'est pas intéressant.")

    def do_stuff(self):
        """Loop for the Listener"""
        while True:
            self.q.get()
            self.q.task_done()

    def on_request_error(self, status_code):
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

def repeater(word: str) -> str:
    """Formating a word who need to be repeated"""
    # Remove first letter if the first letter is a "S" or a "T"
    # Explanation: Trigger word for the repeater is "di" and sometimes it is
    # "dis", sometimes its "dit", that's why we need to remove this 2 letters
    # from the final answer
    if word[0] == 's' or word[0] == 't':
        word = word[1:]

    # Random format from the base answer
    return createBaseAnswers(word)

def getFriends(client: Client, users: list[str]) -> list:
    """Get all friends of choosen users"""
    friends_list = []
    # Get IDs of the user's friends
    for user in users:
        user_id = client.get_user(username=user, user_auth=True).data.id
        friends_list.extend(client.get_users_following(id=user_id, user_auth=True))
    return friends_list[0]

def getIDs(client: Client, users: list[str]) -> list:
    """Get all the ID of users"""
    users_list = []
    # Get IDs of the users
    for user in users:
        users_list.append(client.get_user(username=user, user_auth=True).data)
    return users_list

def seniority(date: str) -> bool:
    """Return True only if the given string date is less than one day old"""
    # Convert string format to datetime format
    datetimeObject = datetime.strptime(date, "%a %b %d %H:%M:%S +0000 %Y")
    # Twitter give us an UTC time
    datetimeObject = datetimeObject.replace(tzinfo = timezone("UTC"))
    # time now in UTC minus the time we got to get the age of the date
    age = datetime.now(timezone("UTC")) - datetimeObject
    # False if older than a day, else True
    return False if age.days >= 1 else True

def generateWords(array: list[str]) -> list:
    """
    Retrieves all possible combinations for the given list and returns the result as a list

    This is used for the filter in the stream (before calling the Listener::on_status)
    """
    quoiListe = []

    for text in array:
        # Add all combinations
        # Example for 'oui': ['OUI', 'OUi', 'OuI', 'Oui', 'oUI', 'oUi', 'ouI', 'oui']
        #
        # -> Depends on: from itertools import product
        # -> Problem : Create a too long list (+1000 words, max is 400)
        # -> Cf. https://developer.twitter.com/en/docs/twitter-api/v1/tweets/filter-realtime/overview
        #
        # quoiListe.extend(list(map(''.join, product(*zip(text.upper(), text.lower())))))

        if text.lower() not in quoiListe:
            # Word in lowercase
            quoiListe.append(text.lower())
        if text.upper() not in quoiListe:
            # Word in uppercase
            quoiListe.append(text.upper())
        if text.capitalize() not in quoiListe:
            # Word capitalized
            quoiListe.append(text.capitalize())

    return quoiListe

def createBaseTrigger(lists: list[list]) -> list:
    """Merges all given lists into one"""
    listing = []
    for liste in lists:
        listing.extend(liste)
    return list(set(listing))

def createBaseAnswers(word: str) -> list:
    """Generates default answers for a given word"""
    irritating_word = [
        "lol",
        "👀",
        "XD",
    ]

    return [
        word,
        f"({word})",
        word.upper(),
        f"{word} {choice(irritating_word)}",
        f"{word}...",
    ]

def createClient(consumer_key, consumer_secret, access_token, access_token_secret) -> Client:
    """Create a client for the Twitter API v2"""
    client = Client(
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        access_token=access_token,
        access_token_secret=access_token_secret
    )

    if keys["VERBOSE"]:
        try:
            client.get_me().data.username
            print(f"Authentification réussie en tant que @{client.get_me().data.username}.", end = " ")
        except:
            print("Erreur d'authentification.")
            exit(1)

    if keys['WHITELIST'] == []:
        whitelist = "Aucun"
    else:
        whitelist = f"@{', @'.join(keys['WHITELIST'])}"
    print(f"Liste des comptes ignorés : {whitelist}.")

    return client

def start():
    """Start the bot"""
    stream = Listener(
        bearer_token=keys["BEARER_TOKEN"],
        client=createClient(
            keys["CONSUMER_KEY"],
            keys["CONSUMER_SECRET"],
            keys["TOKEN"],
            keys["TOKEN_SECRET"],
        ),
        users=keys["PSEUDOS"],
        forcelist=keys["FORCELIST"],
    )

    # TODO: Break in v2 API : max 25 rule (https://docs.tweepy.org/en/stable/streamrule.html#tweepy.StreamRule)
    # Need research, is it possible to run the stream without filter and still catching everything we want?

    # Only track specifics words
    stream.add_rules([StreamRule(word) for word in triggerWords])
    stream.filter(threaded=True)

if __name__ == "__main__":
    """
    TOKEN is the Access Token available in the Authentication Tokens section under the Access Token and Secret sub-heading
    TOKEN_SECRET is the Access Token Secret available in the Authentication Tokens section under the Access Token and Secret sub-heading
    CONSUMER_KEY is the API Key available in the Consumer Keys section under the API Key and Secret sub-heading
    CONSUMER_SECRET is the API Secret Key available in the Consumer Keys section under the API Key and Secret sub-heading
    BEARER_TOKEN is the Bearer Token available in the Authentication Tokens section under the Bearer Token sub-heading
    --
    PSEUDOS is a list of account you want to listen, all of his·er following (guys followed by PSEUDO) will be sniped
    WHITELSIT is a list of account who are protected from the bot
    FORCELIST is a list of account who are targeted by the bot, if user is in the whitelist, he·r will be ignored
    ---
    VERBOSE enable some debugs log
    """
    # Error message
    errorMessage = "Une erreur survient !"

    # Words who trigger the bot (keys in lowercase)
    base = {
        "quoi": ["quoi", "koi", "quoient"],
        "oui": ["oui", "ui", "wi"],
        "non": ["non", "nn"],
        "nan": ["nan"],
        "hein": ["hein", "1", "un"],
        "ci": ["ci", "si"],
        "con": ["con"],
        "ok": ["ok", "okay", "oké", "k"],
        "ouais": ["ouais", "oué"],
        "comment": ["comment"],
        "mais": ["mais", "mé"],
        "fort": ["fort"],
        "coup": ["coup", "cou"],
        "ça": ["ça", "sa"],
        "bon": ["bon"],
        "qui": ["qui", "ki"],
        "sur": ["sur", "sûr"],
        "pas": ["pas", "pa"],
        "ka": ["ka", "kha"],
        "fais": ["fais", "fait"],
        "tant": ["tant", "temps", "tend", "tends"],
        "et": ["et"],
        "la": ["la", "là"],
        "tki": ["tki"],
        "moi": ["moi", "mwa"],
        "toi": ["toi", "toit"],
        "top": ["top"],
        "jour": ["jour", "bonjour"],
        "ya": ["ya", "y'a"],
        "yo": ["yo"],
        "ni": ["ni"],
        "re": ["re", "reu", "reuh"],
        "quand": ["quand", "kan", "qand", "quan"],
        "sol": ["sol"],
        "vois": ["vois", "voit", "voie", "voi"],
        "akhy": ["akhy", "aquis", "aquit"],
    }

    # Answers for all the triggers (keys in lowercase)
    answers = {
        "quoi": createBaseAnswers("feur")
              + createBaseAnswers("feuse")
              + [
                    "https://twitter.com/Myshawii/status/1423219640025722880/video/1",
                    "https://twitter.com/Myshawii/status/1423219684552417281/video/1",
                    "feur (-isson -ictalope -diatre -uil)",
                    "https://twitter.com/Myshawii/status/1455469162202075138/video/1",
                    "https://twitter.com/Myshawii/status/1552026689101860865/video/1",
                    "https://twitter.com/Myshawii/status/1553112547678720001/photo/1"
              ],

        "oui": createBaseAnswers("stiti")
             + createBaseAnswers("fi"),

        "non": createBaseAnswers("bril"),

        "nan": createBaseAnswers("cy"),

        "hein": createBaseAnswers("deux")
              + createBaseAnswers("bécile")
              + [
                    "2"
                ],

        "ci": createBaseAnswers("tron")
            + createBaseAnswers("prine"),

        "con": createBaseAnswers("combre")
             + createBaseAnswers("gelé")
             + createBaseAnswers("pas"),

        "ok": createBaseAnswers("sur glace"),

        "ouais": createBaseAnswers("stern"),

        "comment": createBaseAnswers("tateur")
                 + createBaseAnswers("tatrice")
                 + createBaseAnswers("dant Cousteau"),

        "mais": createBaseAnswers("on")
                + [
                    "on (-dulation)"
                ],

        "fort": createBaseAnswers("boyard")
                + [
                    "boyard (-ennes)"
                ],

        "coup": createBaseAnswers("teau"),

        "ça": createBaseAnswers("perlipopette")
            + createBaseAnswers("von")
            + createBaseAnswers("pristi")
            + [
                "pristi (-gnasse)"
            ],

        "bon": [
            createBaseAnswers("jour"),
            createBaseAnswers("soir")
        ],

        "qui": createBaseAnswers("wi")
             + createBaseAnswers("mono"),

        "sur": createBaseAnswers("prise"),

        "pas": createBaseAnswers("nini")
             + createBaseAnswers("steur")
             + createBaseAnswers("trimoine")
             + createBaseAnswers("té")
             + createBaseAnswers("stis"),

        "ka": createBaseAnswers("pitaine")
            + createBaseAnswers("pitulation"),

        "fais": createBaseAnswers("rtile"),

        "tant": createBaseAnswers("gente")
              + createBaseAnswers("tation"),

        "et": createBaseAnswers("eint")
            + createBaseAnswers("ain"),

        "la": createBaseAnswers("vabo")
            + createBaseAnswers("vande"),

        "tki": createBaseAnswers("la"),

        "moi": createBaseAnswers("tié")
             + createBaseAnswers("sson")
             + createBaseAnswers("sissure"),

        "toi": createBaseAnswers("lette")
             + createBaseAnswers("ture"),

        "top": createBaseAnswers("inambour"),

        "jour": createBaseAnswers("nal"),

        "ya": createBaseAnswers("hourt"),

        "yo": createBaseAnswers("ghourt")
            + createBaseAnswers("yo"),

        "ni": createBaseAnswers("cotine"),

        "re": createBaseAnswers("pas")
            + createBaseAnswers("veil")
            + createBaseAnswers("tourne"),

        "quand": createBaseAnswers("dide")
               + createBaseAnswers("tal")
               + createBaseAnswers("didat"),

        "sol": createBaseAnswers("itaire"),

        "vois": createBaseAnswers("ture"),

        "akhy": createBaseAnswers("nator"),
    }

    # List of all the trigger words
    universalBase = createBaseTrigger(list(base.values()))

    # List of all the triggers words's variations
    triggerWords = generateWords(universalBase)

    # Loading environment variables
    keys = load(["TOKEN", "TOKEN_SECRET", "CONSUMER_KEY", "CONSUMER_SECRET", "BEARER_TOKEN", "PSEUDOS", "VERBOSE", "WHITELIST", "FORCELIST"])

    # Start the bot
    start()
