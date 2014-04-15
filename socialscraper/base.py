from mechanize import Browser
import random

class BaseScraper(object):
    """The base class for all social media scrapers in the package.

    Handles browser emulation (using mechanize) and user agent selection
    for the browser.
    """

    class ScrapeAccount(object):
        def __init__(self,email_or_username,password):
            self.username = email_or_username
            self.password = password

    default_user_agents = set([
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.107 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.2 (KHTML, like Gecko) Chrome/22.0.1216.0 Safari/537.2',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'Konqueror/3.0-rc4; (Konqueror/3.0-rc4; i686 Linux;;datecode)',
        'Opera/9.52 (X11; Linux i686; U; en)'
    ])

    class _Browser(Browser):
        """Subclass of mechanize.Browser that allows the browser to
        smoothly handle XHTML.
        """
        # disable the html check to allow for XHTML
        def viewing_html(self):
            import mechanize
            mechanize.Browser.viewing_html(self)
            return True

    def __init__(self,user_agents = None):
        """Optionally supply a list of user agents for the browser to
        select from.
        If no user agents are supplied, one is picked from a set of
        sensible defaults (see BaseScraper.default_user_agents).
        """
        self._browser = BaseScraper._Browser()
        self._browser.set_handle_robots(False)
        if user_agents:
            self.user_agents = set(user_agents)
        else:
            self.user_agents = BaseScraper.default_user_agents
        self.set_random_user_agent()

        self.users = []
        return

    def set_user_agent(self,user_agent):
        """Set the browser's current user agent.
        If user_agent is not in the set of user agents maintained by this
        BaseScraper instance, it is added to the set.
        """
        if user_agent not in self.user_agents:
            self.user_agents.add(user_agent)
        self._browser.addheaders = [('User-Agent',user_agent)]
        return

    def set_random_user_agent(self):
        """Pick a random user agent from the set of possible agents."""
        self.set_user_agent(random.choice(list(self.user_agents)))

    def add_user_info(self,email_or_username,password):
        """Set the account information to use when a login is required."""
        self.users.append(BaseScraper.UserAccount(email_or_username,
                                                  password))
        return

    def pick_random_user(self):
        if len(self.users) == 0:
            raise UsageError
        return random.choice(self.users)

class BaseUser(object):
    def __init__(self):
        pass

class FeedItem(object):
    def __init__(self, id, content_timestamp=None,content=None,item_type=None):
        self.type = item_type
        self.id = int(id)
        self.content = content
        self.content_timestamp = content_timestamp
    def __str__(self):
        return "FeedItem<%s>(%i): %s" % (self.type, self.id, self.content)
    def __repr__(self):
        return "FeedItem<%s>(%i): %s" % (self.type, self.id, self.content)


class UsageError(Exception):
    def __init__(self,message=None):
        self.message = message
    def __repr__(self):
        return str(type(self)) + ((": %s" % self.message) if self.message else "")

class ScrapingError(Exception):
    pass
