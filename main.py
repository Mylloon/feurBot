from datetime import datetime
from os import environ
from random import choice
from re import findall, sub

from dotenv import load_dotenv
from tweepy import Client, StreamingClient, StreamRule, Tweet, errors


def load(variables) -> dict:
    """Load environment variables"""
    keys = {}
    load_dotenv()  # load .env file
    for var in variables:
        try:
            if var == "VERBOSE":  # check is VERBOSE is set
                try:
                    if environ[var].lower() == "true":
                        res = True
                except:
                    res = False  # if not its False
            elif var == "WHITELIST":  # check if WHITELIST is set
                try:
                    res = list(set(environ[var].split(",")) - {""})
                except:
                    res = []  # if not its an empty list
            elif var == "FORCELIST":  # check if FORCELIST is set
                try:
                    res = list(set(environ[var].split(",")) - {""})
                except:
                    res = []  # if not its an empty list
            else:
                res = environ[var]
            if var == "PSEUDOS":
                # create a list for the channels and remove blank channels and doubles
                res = list(set(res.split(",")) - {""})
            keys[var] = res
        except KeyError:
            print(
                f"Veuillez définir la variable d'environnement {var} (fichier .env supporté)")
            exit(1)
    return keys


def cleanTweet(tweet: str) -> str | None:
    """Remove all unwanted elements from the tweet"""
    # Convert to lower case
    tweet = tweet.lower()
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
        return None
    # Remove usernames
    tweet = sub(r"@\S+", " ", tweet)
    # Remove everything who isn't a letter/number/space
    tweet = sub(r" *?[^\w\s]+", " ", tweet)
    # Remove element of the word only if the last syllable can be matched
    # (so more words will be answered without adding them manually)
    tweet = sub(r"\S+(?=si|ci)", " ", tweet)

    # Remove key smashing in certains words
    #       uiii      naaaan          quoiiii     noooon          heiiin           siiii
    tweet = sub(
        r"(?<=ui)i+|(?<=na)a+(?<!n)|(?<=quoi)i+|(?<=no)o+(?<!n)|(?<=hei)i+(?<!n)|(?<=si)i+", "", tweet)

    return tweet.strip()


class Listener(StreamingClient):
    """Watch for tweets that match criteria in real-time"""

    def __init__(
        self,
        bearer_token,
        client: Client,
    ):
        super(Listener, self).__init__(bearer_token, wait_on_rate_limit=True)
        self.client = client
        self.cache = {}

    def on_connect(self):
        print(f"Début du scroll sur Twitter...")

    def _get_user(self, uid: int) -> str:
        """Return username by ID, with cache support"""
        # If not cached
        if not uid in self.cache:
            # Fetch from Twitter
            self.cache[uid] = self.client.get_user(
                id=uid, user_auth=True).data.username

        # Return the username
        return self.cache[uid]

    def on_tweet(self, tweet: Tweet):
        # Check if the tweet is not a retweet
        if not tweet.text.startswith("RT @"):
            username = self._get_user(tweet.author_id)
            # Clean the tweet
            lastWord = cleanTweet(tweet.text)

            # Log
            if keys["VERBOSE"]:
                infoLastWord = "dernier mot : "
                newline = "\n"
                match lastWord:
                    case None:
                        infoLastWord += "tweet ignoré car trop de hashtags"
                    case w if len(w) == 0:
                        infoLastWord += "tweet pas intéressant"
                    case _:
                        infoLastWord += f"dernier mot : {lastWord.split()[-1:][0]}"
                        newline = ""
                print(
                    f"Tweet trouvé de {username} ({infoLastWord})...{newline}", end=" ")

            # Ignore a tweet
            if lastWord == None or len(lastWord) == 0:
                return

            # Fetch the last word of the tweet
            lastWord = lastWord.split()[-1:][0]

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
                                answer = answers[mot[0]][0]  # jour
                            else:
                                answer = answers[mot[0]][1]  # soir
                        else:
                            # Normal answer
                            answer = answers[mot[0]]

                # If no answer has been found
                if answer == None:
                    if keys["VERBOSE"]:
                        print(f"{errorMessage} Aucune réponse trouvée.")

                # If an answer has been found
                else:
                    if keys["VERBOSE"]:
                        print(f"Envoie d'un {answer[0]}...", end=" ")
                    try:
                        # Send the tweet with the answer
                        self.client.create_tweet(
                            in_reply_to_tweet_id=tweet.id, text=choice(answer))
                        print(f"{username} s'est fait {answer[0]} !")
                    except errors.Forbidden:
                        if keys["VERBOSE"]:
                            print(
                                f"{errorMessage[:-2]} ! Tweet supprimé ou auteur ({username}) en privé/bloqué.")
            else:
                if keys["VERBOSE"]:
                    print("Annulation car le dernier mot n'est pas intéressant.")

    def on_request_error(self, status_code):
        print(f"{errorMessage[:-2]} ({status_code}) !", end=" ")
        match status_code:
            case 420:
                if keys["VERBOSE"]:
                    print("Déconnecter du flux.")
            case 429:
                if keys["VERBOSE"]:
                    print("En attente de reconnexion...")
            case _:
                # newline
                print("")
        return False


def repeater(word: str) -> str:
    """Formating a word who need to be repeated"""
    # Remove first letter if the first letter is a "S" or a "T"
    # Explanation: Trigger word for the repeater is "di" and sometimes it is
    # "dis", sometimes its "dit", that's why we need to remove this 2 letters
    # from the final answer
    if word[0] == "s" or word[0] == "t":
        word = word[1:]

    # Random format from the base answer
    return createBaseAnswers(word)


def getFriends(client: Client, users: list[str]) -> list:
    """Get all friends of choosen users"""
    friends_list = []
    # Get IDs of the user's friends
    for user in users:
        user_id = client.get_user(username=user, user_auth=True).data.id
        friends_list.extend(client.get_users_following(
            id=user_id, user_auth=True))
    return friends_list[0]


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
        # Assuming the first element of this list is always word, don't change it
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
            print(
                f"Authentification réussie en tant que @{client.get_me().data.username}.\n")

            # Compte ignorés
            if keys["WHITELIST"] == []:
                whitelist = "Aucun"
            else:
                whitelist = f"@{', @'.join(keys['WHITELIST'])}"
            print(f"Liste des comptes ignorés : {whitelist}.")

            # Compte forcés
            if keys["FORCELIST"] == []:
                forcelist = "Aucun"
            else:
                forcelist = f"@{', @'.join(keys['FORCELIST'])}"
            print(f"Liste des comptes forcés : {forcelist}.")

            # Compte aux following suivis
            if keys["PSEUDOS"] == []:
                pseudos = "Aucun"
            else:
                pseudos = f"@{', @'.join(keys['PSEUDOS'])}"
            print(
                f"Les comptes suivis par ces comptes sont traqués : {pseudos}.\n")

            print(
                "Notez que si un compte est dans la whitelist, il sera dans tout les cas ignoré.\n")
        except:
            print("Erreur d'authentification.")
            exit(1)

    return client


def create_rules(tracked_users: list[str]) -> list[str]:
    """Create rules for tracking users, by respecting the twitter API policies"""
    rules = []

    # Repeating rules
    repeat = "-is:retweet lang:fr ("

    # Buffer
    buffer = repeat

    # Track users
    for user in tracked_users:
        # Check if the rule don't exceeds the maximum length of a rule (512)
        # 5 is len of "from:"
        # 1 is len for closing parenthesis
        if len(buffer) + len(user) + 5 + 1 > 512:
            rules.append(buffer[:-4] + ")")
            buffer = repeat
        buffer += f"from:{user} OR "

    if len(buffer) > 0:
        rules.append(buffer[:-4] + ")")

    if len(rules) > 25:
        raise BufferError("Too much rules.")

    return rules


def start():
    """Start the bot"""
    client = createClient(
        keys["CONSUMER_KEY"],
        keys["CONSUMER_SECRET"],
        keys["TOKEN"],
        keys["TOKEN_SECRET"],
    )

    # Only track specifics users
    # Including users in forcelist and removing users in whitelist
    tracked_users = [
        i for i in [
            user.data["username"] for user in getFriends(client, keys["PSEUDOS"])
        ] + keys["FORCELIST"] if i not in keys["WHITELIST"]
    ]

    stream = Listener(keys["BEARER_TOKEN"], client)

    # Gathering rules
    rules = [rule for rule in create_rules(tracked_users)]

    # Check if rules already exists
    old_rules = stream.get_rules().data
    old_rules_values = []
    if old_rules:
        old_rules_values = [rule.value for rule in old_rules]
    need_changes = False
    # Same amount of rules
    if len(old_rules_values) == len(rules):
        for rule in rules:
            # Check if Twitter doesn't know the rule and change rules if needed
            if rule not in old_rules_values:
                need_changes = True
                break
    else:
        need_changes = True

    if need_changes:
        if keys["VERBOSE"]:
            print("Changes needed... ", end=" ")
        # Clean old rules
        if old_rules:
            if keys["VERBOSE"]:
                print("deleting old rules... ", end=" ")
            stream.delete_rules([rule.id for rule in old_rules])

        # Add new rules
        if keys["VERBOSE"]:
            print("sending new filter to Twitter.")
        stream.add_rules([StreamRule(rule) for rule in rules])

    # Apply the filter
    stream.filter(threaded=True, tweet_fields="author_id")


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

    # Loading environment variables
    keys = load(["TOKEN", "TOKEN_SECRET", "CONSUMER_KEY", "CONSUMER_SECRET",
                "BEARER_TOKEN", "PSEUDOS", "VERBOSE", "WHITELIST", "FORCELIST"])

    # Start the bot
    start()
