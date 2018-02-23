from requests import Session
import random
import urllib
import time
import logging.config
from config import LOGGING, USER_AGENTS

logging.config.dictConfig(LOGGING)

logger = logging.getLogger('studomatic-scrapper')

class ScrapeSession(Session):
    """
        Enable enforcing a wait time between requests
        Enable going though a proxy, specified by an url

        Example proxy url format:  protocol://proxyhostname?q=<real-endpoint-goes-here>
    """
    def __init__(self, proxy=None, wait=None):
        self.wait = wait
        self.last_timestamp = 0
        super(ScrapeSession, self).__init__()
        self.proxy = proxy

    def wait_remaining(self):
        """
        Wait the remaining time until <wait> seconds have passed since last request
        """
        if self.wait is not None:
            current = time.time()
            if current < (self.last_timestamp + self.wait):
                wait_delta = (self.last_timestamp + self.wait) - current
                time.sleep(wait_delta)
            self.last_timestamp = time.time()

    def get(self, *args, **kwargs):
        kwargs['http_method'] = super(ScrapeSession, self).get
        return self.call_method(*args, **kwargs)

    def post(self, *args, **kwargs):
        kwargs['http_method'] = super(ScrapeSession, self).post
        return self.call_method(*args, **kwargs)

    def call_method(self, *args, **kwargs):
        user_agent = random.choice(USER_AGENTS)
        self.headers.update({
            'User-Agent': user_agent
        })
        kwargs['timeout'] = 20
        f = kwargs.pop('http_method')
        if self.proxy:
            args[0] = self.proxy + urllib.quote_plus(args[0])
        self.wait_remaining()
        return f(*args, **kwargs)
