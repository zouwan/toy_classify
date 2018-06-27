#!/usr/bin/python
# -*- coding: utf-8 -*- 
import common, urllib2, json, traceback, time, utils, socket, sys

reload(sys)
sys.setdefaultencoding('utf-8') 
socket.setdefaulttimeout(5.0)

USER_AGENT  = "Android\t7.0\tautohome\t8.7.0\tAndroid"
FETCH_INTERVAL = 1

#抓取chexiId这个车系下的所有标签
def get_chexi_koubei_tag(chexiId, brandname, seriesname):
	URL = "https://koubei.app.autohome.com.cn/autov8.6.5/alibi/seriesalibiinfos-pm2-ss%d-st0-p1-s20-isstruct1-o0.json" % chexiId
	send_headers = {
		"User-Agent": USER_AGENT,
		"Connection": "Keep-Alive",
		#"Accept-Encoding": "gzip",
	}
	filename = ""
	try:
		req = urllib2.Request(URL, headers=send_headers)
		cont = urllib2.urlopen(req).read()
		mp = json.loads(cont)
		kbList = mp["result"]["structuredlist"]
		sys.stdout.write("%s\t%s\t" % (brandname.encode("utf-8"), seriesname.encode("utf-8")))
		idx = 0
		for kb in kbList:
			idx += 1
			goodfid = open("good_%d.txt" % idx, "a")
			badfid  = open("bad_%d.txt" % idx, "a")
			summary = kb["Summary"]
			for item in summary:
				sk = int(item["SummaryKey"])
				if sk == 0:
					continue
				cb = item["Combination"]
				flag = ""
				sentKey = int(item["SentimentKey"])
				fid = None 
				if sentKey == 3:
					flag = "+"
					fid = goodfid
				elif sentKey == 2:
					flag = "-"
					fid = badfid
				filename += str(idx)
				volume = item["Volume"]
				sys.stdout.write("%s(%s%s); " % (cb.encode("utf-8"), flag, volume))
				fid.write("%s\t%s\n" % (cb.encode("utf-8"), volume))
			goodfid.close()
			badfid.close()
			sys.stdout.write("\t")
		sys.stdout.write("\n")
	except:
		traceback.print_exc()
	time.sleep(FETCH_INTERVAL)

# 抓取汽车之家brandid对应的口碑标签
def get_brand_tag(brandid):
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
		brandname = mp["result"]["brandname"]
		fctlist = mp["result"]["fctlist"]
		#只考虑在售的
		#otherfctlist = mp["result"]["otherfctlist"]
		#fctlist.extend(otherfctlist)
		for fct in fctlist:
			serieslist = fct["serieslist"]
			for series in serieslist:
				sid = int(series["id"])
				sname = series["name"]
				get_chexi_koubei_tag(sid, brandname, sname)
	except:
		traceback.print_exc()

# 抓取汽车之家所有品牌的口碑标签
def get_brand_list():
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
				get_brand_tag(brandId)
	except:
		traceback.print_exc()

print "品牌	车系名称	综合	最满意	最不满意	空间	动力	操控	油耗	舒适性	外观	内饰	性价比	配置"
get_brand_list()
