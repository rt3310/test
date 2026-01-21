# -*- coding:utf-8 -*-

from net.grinder.script.Grinder import grinder
from net.grinder.script import Test
from java.util import Date
from HTTPClient import NVPair, Cookie, CookieModule, Codecs

from net.grinder.plugin.http import HTTPRequest
from net.grinder.plugin.http import HTTPPluginControl

import json
import random

control = HTTPPluginControl.getConnectionDefaults()
control.timeout = 6000

test1 = Test(1, "dev.kitchenlog.shop")
request1 = test1.wrap(HTTPRequest(url="https://dev.kitchenlog.shop"))

cookies = []

class TestRunner:
	def __init__(self):
		test1.record(TestRunner.__call__)
		headers = [NVPair("Content-Type", "application/json")]
		request = HTTPRequest(url="https://dev.kitchenlog.shop")
		request.setHeaders(headers)
		login_body = {
			"account": "test001",
			"password": "seoarc12",
			"fcmToken": ""
		}
		json_login_body = json.dumps(login_body)
		response = request.POST("/api/v1/auth/sign-in/local", json_login_body)
		data = json.loads(response.getText())
		
		self.accessToken = "Bearer " + data['data']['accessToken']
		grinder.statistics.delayReports=True
		pass

	def before(self):
		for c in cookies: CookieModule.addCookie(c, HTTPPluginControl.getThreadHTTPClientContext())

	def __call__(self):
		self.before()
		
		auth_headers = [
			NVPair("Content-Type", "application/json"),
			NVPair("Authorization", self.accessToken)
		]
		request1.setHeaders(auth_headers)
		params = [
			NVPair("categoryId", "127"),
			NVPair("limit", "10")
		]
		result = request1.GET("/api/v1/foods", params)
		
		if result.getStatusCode() == 200 :
			grinder.logger.info("RESPONSE: %s." %  result.getText())
			data = json.loads(result.getText())
			return
		elif result.getStatusCode() in (301, 302) :
			grinder.logger.warn("Warning. The response may not be correct. The response code was %d." %  result.getStatusCode())
			return
		else :
			grinder.logger.error("Warning. The response may not be correct. The response code was %d." %  result.getStatusCode())
			raise
