from dotenv import load_dotenv
from os import environ
from tweepy import OAuthHandler, API, StreamListener, Stream
from re import sub

quoi = ["quoi", "koi"]

def load(variables):
    """Load env variables."""
    keys = {}
    load_dotenv() # load .env file
    for var in variables:
        try:
            keys[var] = environ[var]
        except KeyError:
            print(f"Please set the environment variable {var} (.env file supported)")
            exit(1)
    return keys

class Listener(StreamListener):
    def __init__(self, api = None):
        super(Listener, self).__init__()
        self.num_tweets = 0
        self.api = api

    def on_status(self, status):
        """Réponse au tweet"""
        tweetText = sub(r' ?\?| ?\!', '', status._json["text"])
        if tweetText.endswith(tuple(quoi)):
            try:
                self.api.update_status(status = 'feur', in_reply_to_status_id = status._json["id"], auto_populate_reply_metadata = True)
            except:
                pass

def main(accessToken, accessTokenSecret, consumerKey, consumerSecret, userID):
    """Main method."""
    auth = OAuthHandler(consumerKey, consumerSecret)
    auth.set_access_token(accessToken, accessTokenSecret)
    
    api = API(auth)

    listener = Listener(api)
    stream = Stream(api.auth, listener)
    user = api.get_user(userID)
    print(f"Scroll sur Twitter avec les abonnés de @{user.screen_name}...")
    stream.filter(follow=[userID], track=quoi, is_async = True)

if __name__ == '__main__':
    """
    TOKEN is the Access Token available in the Authentication Tokens section under Access Token and Secret sub-heading
    TOKEN_SECRET is the Access Token Secret available in the Authentication Tokens section under Access Token and Secret sub-heading
    CONSUMER_KEY is the API Key available in the Consumer Keys section
    CONSUMER_SECRET is the API Secret Key available in the Consumer Keys section
    --
    ID is the ID of the account you want to listen to. The ID is fetchable with this website: https://commentpicker.com/twitter-id.php or others
    """
    keys = load(["TOKEN", "TOKEN_SECRET", "CONSUMER_KEY", "CONSUMER_SECRET", "ID"])
    main(keys["TOKEN"], keys["TOKEN_SECRET"], keys["CONSUMER_KEY"], keys["CONSUMER_SECRET"], keys["ID"])
