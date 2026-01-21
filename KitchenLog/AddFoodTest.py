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
		grinder.statistics.delayReports=True
		pass

	def before(self):
		# login
		headers = [NVPair("Content-Type", "application/json")]
		request = HTTPRequest(url="https://dev.kitchenlog.shop")
		account_number = random.randint(1, 100)
		request.setHeaders(headers)
		login_body = {
			"account": "test{:03d}".format(account_number),
			"password": "seoarc12",
			"fcmToken": ""
		}
		json_login_body = json.dumps(login_body)
		response = request.POST("/api/v1/auth/sign-in/local", json_login_body)
		data = json.loads(response.getText())
		
		self.accessToken = "Bearer " + data['data']['accessToken']
		
		# get categories
		auth_headers = [
			NVPair("Content-Type", "application/json"),
			NVPair("Authorization", self.accessToken)
		]
		request.setHeaders(auth_headers)
		category_response = request.GET("/api/v1/categories")
		data = json.loads(category_response.getText())
		self.categories = data['data']
		for c in cookies: CookieModule.addCookie(c, HTTPPluginControl.getThreadHTTPClientContext())

	def __call__(self):
		self.before()
		
		random_category = random.randint(0, 5)
		random_expiry_alarm = random.randint(1, 6)
		request_json = {
			"name": "신선한 우유",
			"categoryIds": [self.categories[random_category]['id']],
			"storageMethod": "냉장", # Enum 값 (문자열)
			"expiryDate": "2026-02-20T23:59:59",
			"expiryAlarm": random_expiry_alarm,
			"memo": "유통기한 확인 필수"
		}
		
		# multipart/form-data 수동 구성
		boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
		
		body_parts = []
		
		# JSON 파트
		body_parts.append("--%s" % boundary)
		body_parts.append('Content-Disposition: form-data; name="request"')
		body_parts.append('Content-Type: application/json')
		body_parts.append('')
		body_parts.append(json.dumps(request_json))
		
		# 이미지 파트 (빈 파일)
		body_parts.append("--%s" % boundary)
		body_parts.append('Content-Disposition: form-data; name="image"; filename="empty.png"')
		body_parts.append('Content-Type: image/png')
		body_parts.append('')
		body_parts.append('')  # 빈 내용
		
		# 마지막 boundary
		body_parts.append("--%s--" % boundary)
		body_parts.append('')
		
		body = "\r\n".join(body_parts)
		
		headers = [
			NVPair("Content-Type", "multipart/form-data; boundary=%s" % boundary),
			NVPair("Authorization", self.accessToken)
		]
		
		request1.setHeaders(headers)
		result = request1.POST("/api/v1/foods", body)

		if result.getStatusCode() == 201 :
			grinder.logger.info("RESPONSE: %s." %  result.getText())
			data = json.loads(result.getText())
			return
		elif result.getStatusCode() in (301, 302) :
			grinder.logger.warn("Warning. The response may not be correct. The response code was %d." %  result.getStatusCode())
			return
		else :
			grinder.logger.error("Warning. The response may not be correct. The response code was %d." %  result.getStatusCode())
			raise
