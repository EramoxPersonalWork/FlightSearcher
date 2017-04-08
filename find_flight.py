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
import argparse
import json
import codecs

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

class SkyErrorCode(object):
	def __init__(self, resp):
		self.error = resp.status
		print("code is " + str(self.error))

	def isFailure(self):
		return self.error != 200

	def __str__ (self):
		code = self.error
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
		return str(code) + " (" + txt + ")";
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
class ServiceParameter(object):
	def __init__(self, coun, cur, loc, ori, dest, dateOut, dateIn):
		self.country = coun
		self.currency = cur
		self.locale = loc
		self.originPlace = ori
		self.destinationPlace = dest
		self.outboundPartialDate = dateOut
		self.inboundPartialDate = dateIn

	def getUrl(self):
		seq = (self.country, self.currency, self.locale, self.originPlace, self.destinationPlace)
		seq += (self.outboundPartialDate, self.inboundPartialDate)
		return "/".join(seq)

	def __str__(self):
		desc = "Parameter for cache service:"
		return desc

class TravelApiCached(SkyscannerAPI):

	def __init__(self, apiKey):
		super().__init__(apiKey)


	def _browseService(self, service, paramService):
		header = {
			"Accept": "application/json",
		}
		h = Http()
		dataUrl = self.endpoint + "browse" + service + "/v1.0/" + paramService.getUrl() + "?apikey=" + self.apikey
#		print("Poling " + dataUrl)
		resp, content = h.request(dataUrl, "GET")
		errorCode = SkyErrorCode(resp)
		print("Content:\n" + str(content))
		print("Resp:\n" + str(resp))
		print("ErrorCode:" + str(errorCode))

		if errorCode.isFailure():
			return None

		parser = SkyJSONParser(content)
		parser.getCurrency()

		return content;

	def browseQuotes(self, paramService):
		return self._browseService("quotes", paramService)

	def browseRoutes(self, paramService):
		return self._browseService("routes", paramService)

	def browseDates(self, paramService):
		return self._browseService("dates", paramService)

	def browseDatesGrid(self, paramService):
		return self._browseService("grid", paramService)

class SkyJSONParser(object):
	def __init__(self, content):
		self.loaded = json.loads(content.decode())
		print("Content loaded: " + str(self.loaded))

#	def getPlaces(self):

	def getCurrency(self):
		jsonCur = self.loaded["Currencies"][0]
		print("Currency: " + str(jsonCur))
		cur = Currency(jsonCur["Code"],
				jsonCur["Symbol"],
				jsonCur["ThousandsSeparator"],
				jsonCur["DecimalSeparator"],
				jsonCur["SymbolOnLeft"],
				jsonCur["SpaceBetweenAmountAndSymbol"],
				jsonCur["RoundingCoefficient"],
				jsonCur["DecimalDigits"])
		print("cur: " + str(cur))
		return cur

#	def getCarrier(self):

class Place(object):
	def __init__(self, placeId, iataCode, name, type, skyscannerCode,
			cityName, cityId, countryName):
		self.placeId = placeId

class Carrier(object):
	def __init__(self, carrierId, name):
		self.carrierId = carrierId
		self.name = name

class Value(object):
	def __init__(self, units, decimals):
		self.units = units
		self.decimals = decimals

	def printValue(self, currency):
		return currency.printValue(self)

	def getUnits(self):
		return self.units

	def getDecimals(self):
		return self.decimals

	def __str__(self):
		return str(self.units) + " " + str(self.decimals)

class Currency(object):
	def __init__(self, code, symbol,
			thousandsSeparator, decimalSeparator,
			symbolOnLeft, spaceBetweenAmountAndSymbol,
			roundingCoefficient, decimalDigits):
		self.code = code
		self.symbol = symbol
		self.thousandsSeparator = thousandsSeparator
		self.decimalSeparator = decimalSeparator
		self.symbolOnLeft = symbolOnLeft
		self.spaceBetweenAmountAndSymbol = spaceBetweenAmountAndSymbol
		self.roundingCoefficient = roundingCoefficient
		self.decimalDigits = decimalDigits

	def __str__(self):
		tempV = Value("0123456789", "ABCDEF")
		print("tempC: " + str(tempV))
		return self.code + ": " + self.printValue(tempV)

	def printValue(self, value):
		line = ""
		if self.symbolOnLeft:
			line += self.symbol
			if self.spaceBetweenAmountAndSymbol:
				line += " "

		strUnits = str(value.getUnits())
		unitDigits = 3

		print("strU: " + strUnits)

		start = 0
		end = len(strUnits) % unitDigits
		line += strUnits[start : end]
		while end < len(strUnits):
			if end != 0:
				line += self.decimalSeparator
			start = end
			end += unitDigits
			line += strUnits[start : end]

		print("formatees: " + line)

		line += self.decimalSeparator

		line += str(value.getDecimals())[0 : self.decimalDigits]

		if not self.symbolOnLeft:
			line += self.symbol
			if self.spaceBetweenAmountAndSymbol:
				line += " "

		return line

	def getValue(self, string):
		elm = string.split(self.decimalSeparator)
		return Value(elm[0],elm[1])


class SkyContent(object):
	def __init__(self, content):
		self.content = content

#	def process(self):

#	def processCurrency(self):

#	def processCarriers(self):

#	def processPlaces(self):

parser = argparse.ArgumentParser(description='Find a flight sing Skyscanner API')
parser.add_argument('--key', help='Skyscanner API key', required=True)

def main(argv=None):
	if argv is None:
		argv = sys.argv

	args = vars(parser.parse_args())

#	tal = TravelApiLive()
#	tal.create_session()
	tac = TravelApiCached(args["key"])
	param = ServiceParameter("UK", "GBP", "en-GB", "EDI", "LHR", "2017-05-30", "2017-06-02")
	print("param: " + str(param) + param.getUrl())
#	print("param: " + str(param))
#	print("browsing quotes")
#	tac.browseQuotes(param)
#	print("browsing routes")
#	tac.browseRoutes(param)
#	print("browsing dates")
#	tac.browseDates(param)
	print("browsing dates as grid")
	res = tac.browseDatesGrid(param)

	return 0

if __name__ == '__main__':
	sys.exit(main())
