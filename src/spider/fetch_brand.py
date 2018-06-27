#!/usr/bin/python
# -*- coding: utf-8 -*- 
import common, urllib2, json, traceback, time, utils, socket, sys

reload(sys)
sys.setdefaultencoding('utf-8') 
socket.setdefaulttimeout(5.0)

USER_AGENT  = "Android\t7.0\tautohome\t8.7.0\tAndroid"
FETCH_INTERVAL = 1

# 抓取汽车之家所有品牌id与品牌名称
def get_brand_list():
	URL = "https://cars.app.autohome.com.cn/cars_v8.8.5/cars/brands-pm2.json?pluginversion=9.0.5"
	send_headers = {
		"User-Agent": USER_AGENT,
		"Connection": "Keep-Alive",
		#"Accept-Encoding": "gzip",
	}
	try:
		req = urllib2.Request(URL, headers=send_headers)
		cont = urllib2.urlopen(req).read()
		mp = json.loads(cont)
		#厂商列表
		fctList = mp["result"]["fctlist"]
		for letterBrand in letterBrandList:
			letterBrand = letterBrand["list"]
			for brand in letterBrand:
				brandid = brand["id"]
				brandname = brand['name']

				sys.stdout.write("%s\t%s\n" % (brandid,brandname))
				#break
	except:
		traceback.print_exc()


get_brand_list()