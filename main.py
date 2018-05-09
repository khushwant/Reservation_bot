import webapp2
import json
import requests
import requests_toolbelt.adapters.appengine
import os
import traceback
from datastore import DBHelper
import config
import logging
import urllib
import urllib2
from google.appengine.api import urlfetch
from reservation_bot import handle_updates
#from reservation_bot import start_bot


logger = logging.getLogger("reservation-bot")
logger.setLevel(logging.DEBUG)


def parseConfig():
    global BASE_URL, URL_OWM, HOOK_TOKEN, PROJECT_ID

    TOKEN = config.TOKEN

    BASE_URL = "https://api.telegram.org/bot" + TOKEN + "/"

    # OWN_KEY = config.OWM_KEY
    # URL_OWM = "http://api.openweathermap.org/data/2.5/weather?appid={}&units=metric".format(OWM_KEY)

    HOOK_TOKEN = config.HOOK_TOKEN
    PROJECT_ID = config.PROJECT_ID
    logger.info("Setting ProjectID to : %s" % config.PROJECT_ID)
    logger.info("ProjectID set to : %s" % PROJECT_ID)


def setTimeout(numSec = 60):
    urlfetch.set_default_fetch_deadline(numSec)


requests_toolbelt.adapters.appengine.monkeypatch()
db = DBHelper()


def formatResp(obj):
    parsed = json.load(obj)
    return json.dumps(parsed, indent=4, sort_keys=True)


class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Bot Initialized\n')


class DataInfoPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'

        #Show Entities
        self.response.write('\nENTITIES\n')
        booking, logs = db.get_all()
        self.response.write('\n<b>Booking table</b>\n')
        for r in booking:
            self.response.write('{}\n'.format(r))
        self.response.write('\n<b>Logs table</b>\n')
        for r in logs:
            self.response.write('{}\n'.format(r))


#-----------------Handler functions------------------------

class MeHandler(webapp2.RequestHandler):
    def get(self):
        setTimeout()
        parseConfig()
        url = BASE_URL + "getMe"
        respBuf = urllib2.urlopen(url)
        self.response.headers["Content-Type"] = "text/plain"
        self.response.write(formatResp(respBuf))


# Get information about webhook status
class GetWebhookHandler(webapp2.RequestHandler):
    def get(self):
        setTimeout()
        parseConfig()

        url = BASE_URL + "getWebhookInfo"
        respBuf = urllib2.urlopen(url)

        self.response.headers["Content-Type"] = "text/plain"
        self.response.write(formatResp(respBuf))


# Set a webhook url for Telegram to POST to
class SetWebhookHandler(webapp2.RequestHandler):
    def get(self):
        setTimeout()
        parseConfig()

        hookUrl = "https://%s.appspot.com/TG%s" % (PROJECT_ID, HOOK_TOKEN)
        logger.info("Setting new webhook to: %s" % hookUrl)
        respBuf = urllib2.urlopen(BASE_URL + "setWebhook", urllib.urlencode({
            "url": hookUrl
        }))
        self.response.headers["Content-Type"] = "text/plain"
        self.response.write(formatResp(respBuf))


class WebhookHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write("hey")

    def post(self):
        setTimeout()
        parseConfig()
        logger.info("Received request: %s from %s" % (self.request.url, self.request.remote_addr))
        if HOOK_TOKEN not in self.request.url:
            # Not coming from Telegram
            logger.error("Post request without token from IP: %s" % self.request.remote_addr)
            return

        json_content = json.loads(self.request.body)
        try:
            # start_bot()
            logger.info("Received json: %s"% json_content)
            handle_updates(json_content)
        except:
            logger.info("Error found in handling")
            tb = traceback.format_exc()
            db.add_log(str(tb))


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/info', DataInfoPage),
    ('/set_webhook', SetWebhookHandler),
    ('/get_webhook', GetWebhookHandler),
    (r'/TG.*', WebhookHandler),
    ('/me', MeHandler)
], debug=True)
