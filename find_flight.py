#!/usr/bin/env
# coding: utf-8


#polling_session_data = {
#	"apiKey": skyApiKey,
#}
#poling_pricing_data(polling_address, polling_session_data)

from httplib2 import Http
try:
	from urllib import urlencode
except ImportError:
	from urllib.parse import urlencode

from lxml import etree
from io import StringIO
import sys
import getopt

class SkyscannerAPI(object):
	'Class to handle requests to Skyscanner REST API'
	endpoint = "http://partners.api.skyscanner.net/apiservices/"

	def __init__(self, apiKey):
#		import MySQLdb
#		self.db = MySQLdb.connect("localhost","root","root","testdb" )
#		cursor = db.cursor()
#		cursor.execute("SELECT VERSION()")
#		data = cursor.fetchone()
#		print("Database version : %s " % data)
		self.apikey = apiKey
		print(__name__ + " constructed")

	def __del__(self):
		#print("Closing DB")
		#self.db.close()
		print(__name__ + " destroyed")

	def str_resp (self, resp):
		code = resp.status
		print("code is " + str(code))
		txt = "Unknow"
		if code == 200:
			txt = "Success"
		elif code == 204:
			txt = "No content"
		elif code == 304:
			txt = "Not modified"
		elif code == 400:
			txt = "Bad Request"
		elif code == 403:
			txt = "Forbidden"
		elif code == 410:
			txt = "Gone"
		elif code == 429:
			txt = "Too many Request"
		elif code == 500:
			txt = "Server error"

		print("String is " + txt)
		return str(code) + "(" + resp.reason + ") -> (" + txt + ")";
#print_code("test", 200)
#print_code("test2", 201)
#print_code("test3", 400)
#print_code("test4", 403)
#print_code("test5", 429)
#print_code("test6", 500)

class TravelApiLive(SkyscannerAPI):

	def __init__(self, apiKey):
		super(TravelApiLive, self).__init__(apiKey)

# Get URL format
# http://partners.api.skyscanner.net/apiservices/pricing/v1.0/{sessionKey}?apiKey={apiKey}
#
# Heqder
# HTTP Content-Type header: ‘application/x-www-form-urlencoded’.
# HTTP Accept header: ‘application/json’ or ‘application/xml’.
	def create_session (self):
		header = {
			"Content-Type": "application/x-www-form-urlencoded",
#			"X-Forwarded-For": "90.116.243.103",
			"Accept": "application/xml",
		}

#	import xml.etree.ElementTree as ET

		h = Http()
		req = self.create_session_data()
		postAddress = self.endpoint + "/pricing/v1.0"
		req_encoded = urlencode(req)
		print("Header: ", header)
		print("Encoded: ", req_encoded)
		print("to : ", postAddress)
		resp, content = h.request(postAddress, "POST", req_encoded, header)

		print("Content:", content)
		print("Resp:", self.str_resp(resp))
		print("Full Resp:", resp)

		poll_address = resp["location"]

		self.poll_address = poll_address
		return poll_address;

	def create_session_data(self):
		opening_session_data = {
			"country": "UK",
			"currency": "GBP",
			"locale": "en-GB",
			"originplace": "EDI",
			"destinationplace": "LHR",
			"outbounddate": "2017-05-30",
			"inbounddate": "2017-06-02",
			"cabinclass": "Economy",
			"adults": 1,
			"children": 0,
			"infants": 0,
			"apiKey": "empty",
			"locationschema": "iata",
		}
		opening_session_data["apiKey"] = self.apiKey
		print("Session data created: " + str(opening_session_data))
		return opening_session_data
#polling_address = create_session(opening_session_data)
#print("Polling from " + polling_address)
#print("Start polling")



	def poling_ref_data (type):

		h = Http()
		dataUrl = self.endpoint + "/reference/v1.0/" + type + "?apiKey=" + self.apiKey
		print("Poling [" + type + "] from " + dataUrl)
		resp, content = h.request(dataUrl, "GET")
		print("Content:", content)
		print("Resp:", self.str_resp(resp))

		return;
# Tested the qpikey -> OK
#poling_ref_data("locales")
#poling_ref_data("currencies")


# Request details
# Posting URL: http://partners.api.skyscanner.net/apiservices/pricing/v1.0
	def poling_pricing_data (self, poll_addr, param):

		h = Http()
		dataUrl = poll_addr + "?apiKey=" + skyApiKey
		print("Poling prices from " + dataUrl)
		resp, content = h.request(dataUrl, "GET")
		#print("Content:", content
		print("Resp:", self.str_resp(resp))

	# Output xml to file
#	root = etree.fromstring(xml)
#	parser = etree.XMLParser(resolve_entities=False, strip_cdata=False)
#	formatted = etree.parse(StringIO(unicode(content)), parser)
#	formatted.write("Result.xml", pretty_print=True, encoding='utf-8')

		with open('Res.xml', 'w') as f:
			f.write(content)

		return;


class TravelApiCached(SkyscannerAPI):

	def __init__(self, apiKey):
		super(TravelApiCached, self).__init__(apiKey)

	def buildServiceParameter(self, coun, cur, loc, ori, dest, dateOut, dateIn):
		serviceParameter = {
			"country": coun,
			"currency": cur,
			"locale": loc,
			"originPlace": ori,
			"destinationPlace": dest,
			"outboundPartialDate": dateOut,
			"inboundPartialDate": dateIn,
		}
#		print("Service parameter crated:" + str(serviceParameter))
		return serviceParameter

	def _buildUrlFromServiceParam(self, serviceParam):
		url = serviceParam["country"] + "/"
		url += serviceParam["currency"] + "/"
		url += serviceParam["locale"] + "/"
		url += serviceParam["originPlace"] + "/"
		url += serviceParam["destinationPlace"] + "/"
		url += serviceParam["outboundPartialDate"] + "/"
		url += serviceParam["inboundPartialDate"]
		return url

	def _browseService(self, service, paramService):
		header = {
			"Accept": "application/json",
		}
		h = Http()
		serviceUrl = self._buildUrlFromServiceParam(paramService)
		dataUrl = self.endpoint + "browse" + service + "/v1.0/" + serviceUrl + "?apikey=" + self.apiKey
#		print("Poling " + dataUrl)
		resp, content = h.request(dataUrl, "GET")
#		print("Content:", content)
		print("Resp:", self.str_resp(resp))

		return content;

	def browseQuotes(self, paramService):
		self._browseService("quotes", paramService)

	def browseRoutes(self, paramService):
		self._browseService("routes", paramService)

	def browseDates(self, paramService):
		self._browseService("dates", paramService)

	def browseDatesGrid(self, paramService):
		self._browseService("grid", paramService)

def main(argv=None):
	if argv is None:
		argv = sys.argv

	try:
		opts, args = getopt.getopt(argv[1:], "hk:", ["help", "key="])
        # more code, unchanged
	except getopt.GetoptError as err:
		print(err.msg, file=sys.stderr)
		print("for help use --help", file=sys.stderr)
		return 1

#	tal = TravelApiLive()
#	tal.create_session()
	tac = TravelApiCached()
	param = tac.buildServiceParameter("UK", "GBP", "en-GB", "EDI", "LHR", "2017-05-30", "2017-06-02")
	print("param: " + str(param))
	print("browsing quotes")
	tac.browseQuotes(param)
	print("browsing routes")
	tac.browseRoutes(param)
	print("browsing dates")
	tac.browseDates(param)
	print("browsing dates as grid")
	tac.browseDatesGrid(param)

	return 0

if __name__ == '__main__':
	sys.exit(main())
