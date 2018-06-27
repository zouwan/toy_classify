#!/usr/bin/python
# -*- coding: utf-8 -*- 

import common, urllib2, json, traceback, time, utils, socket, sys

reload(sys)
sys.setdefaultencoding('utf-8') 
socket.setdefaulttimeout(5.0)

USER_AGENT  = "Android\t7.0\tautohome\t8.7.0\tAndroid"
FETCH_INTERVAL = 1

class PriceInfo:
	def __init__(self, brand, chexiname, chexiid, low, high):
		self.brand = brand
		self.chexiname = chexiname
		self.chexiid = chexiid
		self.low = low
		self.high = high
		sys.stdout.write("%s\t%s\t%s\t%d\t%d\n" % (brand.encode("utf-8"), chexiname.encode("utf-8"), chexiid, low, high))
		sys.stdout.flush()

def proc_name(s):
	ss = s.strip(" ").lower()
	ss = ss.replace(" ", "")
	ss = ss.replace("(", "")
	ss = ss.replace(")", "") 
	return ss

prices = []

def get_brand_price(brandid):
	global prices
	URL = "http://cars.app.autohome.com.cn/cars_v8.7.0/cars/seriesprice-pm2-b%d-t16-v8.7.2-c110100.json?pluginversion=8.7.2" % brandid
	send_headers = {
		"User-Agent": USER_AGENT,
		"Connection": "Keep-Alive",
		#"Accept-Encoding": "gzip",
	}
	try:
		req = urllib2.Request(URL, headers=send_headers)
		cont = urllib2.urlopen(req).read()
		mp = json.loads(cont)
		brandname = mp["result"]["brandname"].strip(" ")
		##brandname = proc_name(brandname)
		fctlist = mp["result"]["fctlist"]
		otherfctlist = mp["result"]["otherfctlist"]
		fctlist.extend(otherfctlist)
		for fct in fctlist:
			serieslist = fct["serieslist"]
			for series in serieslist:
				sid = int(series["id"])
				sname = series["name"]
				##sname = proc_name(sname)
				##sname = sname.replace(brandname, "")
				pricerange = series["price"].strip(" ")
				idx = pricerange.find(u"万")
				if idx > 0:
					pricerange = pricerange[0:idx]
				cols = pricerange.split("-")
				low = 0.0
				high = 0.0
				if len(cols) >= 1:
					try:
						low = float(cols[0])
					except:
						pass
				if len(cols) == 1:
					try:
						high = float(cols[0])
					except:
						pass
				if len(cols) >= 2:
					try:
						high = float(cols[1])
					except:
						pass
				prices.append(PriceInfo(brandname, sname, sid, low, high))
	except:
		traceback.print_exc()

def fetch_brand_list_price():
	URL = "https://cars.app.autohome.com.cn/cars_v8.7.0/cars/brands-pm2.json?pluginversion=8.7.2"
	send_headers = {
		"User-Agent": USER_AGENT,
		"Connection": "Keep-Alive",
		#"Accept-Encoding": "gzip",
	}
	try:
		req = urllib2.Request(URL, headers=send_headers)
		cont = urllib2.urlopen(req).read()
		mp = json.loads(cont)
		letterBrandList = mp["result"]["brandlist"]
		for letterBrand in letterBrandList:
			letterBrand = letterBrand["list"]
			for brand in letterBrand:
				brandId = brand["id"]
				get_brand_price(brandId)
	except:
		traceback.print_exc()

def less_equal(a, b, num):
	aa = a.replace("进口", "")
	bb = b.replace("进口", "")
	minlen = len(aa)
	if minlen > len(bb):
		minlen = len(bb)
	return (aa[0:minlen] == bb[0:minlen] or aa[-minlen:] == bb[-minlen:]) and minlen > num

def fill_db_info():
	outfile = "chexi_db_price"
	outfid = open("outfile", "w")
	for line in open("chexi_db").readlines():
		try:
			line = line.strip("\n")
			cols = line.split("\t")
			if len(cols) != 5:
				sys.stderr.write("skip %s" % line)
				continue
			id1 = cols[0]
			brandname = proc_name(cols[1])
			id2 = cols[2]
			chexipat = proc_name(cols[3])
			chexipat = chexipat.replace(brandname, "")
			prefixlow = 0
			prefixhigh = 0
			prefixchexiid = -1
			dstprefixbrand = ""
			dstprefixchexi = ""
			dstbrand = ""
			dstchexi = ""
			chexiid = -1
			low = 0
			high = 0
			mode = "NOHIT"
			if len(brandname) == 0 or len(chexipat) == 0:
				continue
			for price in prices:
				if len(price.brand) == 0 or len(price.brand) == 0:
					continue
				curbrand = price.brand.encode("utf-8")
				curbrand = proc_name(curbrand)
				curchexi = price.chexiname.encode("utf-8")
				curchexi = proc_name(curchexi)
				curchexi = curchexi.replace(curbrand, "")
				hit = curbrand == brandname and curchexi == chexipat
				if not hit:
					hit = (curbrand + curchexi == brandname + chexipat)
				if hit:
					low = price.low
					high = price.high
					mode = "HIT-OK"
					chexiid = price.chexiid
					dstbrand = price.brand
					dstchexi = price.chexiname
					if price.low <= 0 or price.high <= 0:
						mode = "HIT-OFF"
					break
				#车牌一样, 车系模糊匹配
				if curbrand == brandname and less_equal(curchexi, chexipat, 0):
					prefixlow = price.low
					prefixhigh = price.high
					prefixchexiid = price.chexiid
					dstprefixbrand = price.brand
					dstprefixchexi = price.chexiname
				#车系比较长，且一样，也算模糊匹配
				elif less_equal(curbrand + curchexi, chexipat, 6) or less_equal(curchexi, brandname + chexipat, 6):
					prefixlow = price.low
					prefixhigh = price.high
					prefixchexiid = price.chexiid
					dstprefixbrand = price.brand
					dstprefixchexi = price.chexiname
				elif less_equal(curbrand, brandname, 4) and less_equal(curchexi, chexipat, 1):
					prefixlow = price.low
					prefixhigh = price.high
					prefixchexiid = price.chexiid
					dstprefixbrand = price.brand
					dstprefixchexi = price.chexiname
			if chexiid < 0 and prefixchexiid > 0:
				mode = "LESS-OK"
				chexiid = prefixchexiid
				low = prefixlow
				high = prefixhigh
				if low<= 0 and high <= 0:
					mode = "LESS-OFF"
				dstbrand = dstprefixbrand
				dstchexi = dstprefixchexi
			link = ""
			if chexiid > 0:
				link = "https://www.autohome.com.cn/%d/#pvareaid=103177" % chexiid
			outfid.write("%s\t%s\t%s\t%s\t%f\t%f\t%s\t%d\t%s\t%s\t%s\n" % (id1, cols[1], id2, cols[3], low, high, mode, chexiid, dstbrand.encode("utf-8"), dstchexi.encode("utf-8"), link))
			outfid.flush()
		except:
			traceback.print_exc()

#print "品牌	车系名称	综合	最满意	最不满意	空间	动力	操控	油耗	舒适性	外观	内饰	性价比	配置"
##get_brand_tag(33)
##get_chexi_koubei_tag(146)
#get_brand_list()

fetch_brand_list_price()
fill_db_info()
