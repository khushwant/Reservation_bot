import webapp2
import json
import requests
import requests_toolbelt.adapters.appengine
import os
import traceback
from datastore import DBHelper
from reservation_bot import handle_updates
from reservation_bot import start_bot
import config
import urllib
import urllib2
import logging

requests_toolbelt.adapters.appengine.monkeypatch()

db = DBHelper()

def formatResp(obj):
    parsed = json.load(obj)
    return json.dumps(parsed, indent=4, sort_keys=True)


def parseConfig():
	global BASE_URL, URL_OWM, HOOK_TOKEN, PROJECT_ID

	TOKEN = config.TOKEN

	BASE_URL = "https://api.telegram.org/bot" + TOKEN + "/"

    # OWN_KEY = config.OWM_KEY
	# URL_OWM = "http://api.openweathermap.org/data/2.5/weather?appid={}&units=metric".format(OWM_KEY)

	HOOK_TOKEN = c.get("Settings", "HOOK_TOKEN")
	# PROJECT_ID = c.get("Settings", "PROJECT_ID")

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

class MeHandler(webapp2.RequestHandler):
    def get(self):
        # setTimeout()
        parseConfig()

        url = config.BASE_URL + "getMe"
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


class WebHookHandler(webapp2.RequestHandler):
	def get(self):
		self.response.write("hey")

	def post(self):
		json_content = json.loads(self.request.body)
		try:
			start_bot()
			# handle_updates(json_content)
		except:
			tb = traceback.format_exc()
			db.add_log(str(tb))


app = webapp2.WSGIApplication([
	('/', MainPage),
	('/info', DataInfoPage),
	('/webhook/bot567256577:AAELf6Y4vOqYUfdyPMhOSiUedKQ-rZt6Lqs', WebHookHandler),
	('/me', MeHandler)
], debug=True)
