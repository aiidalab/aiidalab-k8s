from oauthenticator import OAuthLoginHandler
from oauthenticator.generic import GenericOAuthenticator

from tornado.auth import OAuth2Mixin

from jupyterhub.handlers.login import LogoutHandler
from jupyterhub.utils import url_path_join


MARKETPLACE_PROTOCOL = 'https'
# NOTE: final Marketplace deployment should be hosted at 'the-marketplace-project.eu'
MARKETPLACE_HOSTS = {
    'production': "materials-marketplace.eu"
}
MARKETPLACE_HOST = MARKETPLACE_HOSTS['production']
MARKETPLACE_URL = f"{MARKETPLACE_PROTOCOL}://{MARKETPLACE_HOST}"


class MarketplaceMixin(OAuth2Mixin):

    _OAUTH_AUTHORIZE_URL = f"{MARKETPLACE_URL}/oauth/oauth2/auth"

    _OAUTH_ACCESS_TOKEN_URL = f"{MARKETPLACE_URL}/oauth/oauth2/token"


class MarketplaceOAuthLoginHandler(OAuthLoginHandler, MarketplaceMixin):
    """Standard OAuthLoginHandler, with assigned Marketplace authorize and
    callback urls"""
    pass


class MarketplaceLogoutHandler(LogoutHandler):
    """LogoutHandler class that removes username from local database
    after session has ended"""

    def get(self):
        """Log a user out by clearing their login cookie and removing
        them from the JupyterHub's database """

        user = self.get_current_user()

        if user:
            self.log.info("User logged out: %s", user.name)
            self.clear_login_cookie()

            for name in user.other_user_cookies:
                self.clear_login_cookie(name)

            user.other_user_cookies = set([])

            # This is the only line that differs from the super class
            # method. It simply removes the user from the JupyterHub
            # database upon logging out.
            self.remove_user_from_db(user)

            self.statsd.incr('logout')

        self.redirect(url_path_join(self.hub.server.base_url, 'login'), permanent=False)

    def remove_user_from_db(self, user):
        """Removes and non-admin users from JupyterHub's database"""
        if not user.admin:
            self.db.delete(user)
            self.db.commit()
            self.log.info("Removed user with id {}".format(user.id))


class MarketplaceOAuthenticator(GenericOAuthenticator):
    """A GenericOAuthenticator with assigned LoginHandler containing Marketplace
    specific urls"""

    login_service = "Marketplace"

    login_handler = MarketplaceOAuthLoginHandler

    # You only need to assign this attribute if you want to provide
    # a custom logout handler (such as implemented above)
    logout_handler = MarketplaceLogoutHandler

    scope = ["openid", "offline"]

    userdata_url = f"{MARKETPLACE_URL}/oauth/userinfo"

    token_url = f"{MARKETPLACE_URL}/oauth/oauth2/token"

    def username_key(self, resp_json):
        """Returns either Marketplace username or user id from
        JWT, depending on which information is present"""

        # Check whether Marketplace username is included"""
        if 'userid' in resp_json:
            return resp_json['userid']

        # Otherwise return id
        return resp_json['sub']

    def normalize_username(self, username):
        """Adds pre-processing of dictionary arguments"""
        if isinstance(username, dict):
            username = username['name']
        return super(MarketplaceOAuthenticator, self).normalize_username(username)

    def logout_url(self, base_url):
        """Use unique url for custom LogoutHandler"""
        return url_path_join(base_url, 'oauth_logout')

    def get_handlers(self, app):
        """Include custom LogoutHandler class"""
        handlers = super().get_handlers(app)
        handlers += [('/oauth_logout', self.logout_handler)]
        return handlers
