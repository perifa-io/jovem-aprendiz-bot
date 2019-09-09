from twython import Twython
from conf.settings import TWITTER_APP_KEY, TWITTER_APP_SECRET


class Twitter:
    def __init__(self, app_key=TWITTER_APP_KEY, app_secret=TWITTER_APP_SECRET):
        self.app_key = app_key
        self.app_secret = app_secret
        self.client = Twython(self.app_key, self.app_secret)

    def update_client(self):
        self.client = Twython(
            self.app_key,
            self.app_secret,
            self.oauth_token,
            self.oauth_token_secret
        )

    def login(self):
        auth = self.client.get_authentication_tokens()
        self.oauth_token = auth['oauth_token']
        self.oauth_token_secret = auth['oauth_token_secret']

        return auth['auth_url']

    def confirm_login(self, oauth_verifier):
        self.update_client()
        login_res = self.client.get_authorized_tokens(oauth_verifier)
        self.oauth_token = login_res['oauth_token']
        self.oauth_token_secret = login_res['oauth_token_secret']

        self.update_client()
        return self.client.verify_credentials()
