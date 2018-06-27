#!/usr/bin/python
# -*- coding: utf-8 -*- 

import common, urllib2, json, traceback, time, utils, socket

FETCH_COUNT    = 10000
FETCH_INTERVAL = 1

LAST_UID    = 13127914
DEVICE_ID   = 863696036910579
USER_AGENT  = "Android\t7.0\tautohome\t8.7.0\tAndroid"

socket.setdefaulttimeout(5.0) 
ret = {}
count =  0
lastid = ""
while count < FETCH_COUNT:
	url = "https://chejiahao.app.autohome.com.cn/chejiahao_v1_4_0/newspf/NPNewsList.json?a=2&pm=2&v=8.7.0&au=&lastid=%s&lastuid=%s&size=30&type=1&deviceId=%s&followUIds=" % (lastid, LAST_UID, DEVICE_ID)
	send_headers = {
		"User-Agent": USER_AGENT,
		"Connection": "Keep-Alive",
		#"Accept-Encoding": "gzip",
	}
	try:
		req = urllib2.Request(url,headers=send_headers)
		cont = urllib2.urlopen(req).read()
		mp = json.loads(cont)
		lastid = mp["result"]["lastid"]
		if len(lastid) == 0:
			common.LogErr("%s: lastid is null" % url)
			break
		newslist = mp["result"]["newslist"]
		if len(newslist) == 0:
			common.LogErr("%s: newslist is null" % url)
			break
		#print cont
		for item in newslist:
			title = item["title"].encode("utf-8")
			#print "title:", title
			#播放/阅读
			pv = utils.ConvertToInt(item.get("pV"))
			#点赞
			praisenum = utils.ConvertToInt(item.get("praisenum"))
			#回复
			replycount = utils.ConvertToInt(item.get("replycount"))
			#类别
			mediatype = utils.ConvertToInt(item.get("mediatype"))
			#print "mediatype", mediatype
			#会话标示
			newsid = item["newsid"]
			#内容形式：长文
			detailurl = "https://chejiahaonc.app.autohome.com.cn/chejiahao_v1_4_0/newspf/news/nplongarticle-pm2-n%d-rct0-v8.7.0-ish1.json" % newsid
			#内容形式：视频
			if mediatype == 3:
				detailurl = "https://chejiahaonc.app.autohome.com.cn/chejiahao_v1_4_0/newspf/news/npvideofinalpage-pm2-n%s-ntwifi-w1080-rct0-v8.7.0-ish1.json" % newsid
			#内容形式：轻文
			if mediatype == 2:
				detailurl = "https://chejiahaonc.app.autohome.com.cn/chejiahao_v1_4_0/newspf/news/npshortarticle-pm2-n%s-rct0-v8.7.0-ish1.json" % newsid
			#print "detailurl", detailurl
			detailreq = urllib2.Request(detailurl, headers=send_headers)
			detailcont = urllib2.urlopen(detailreq).read()
			flag = "autohome://platformlabel/"
			classfy = []
			classfystr = ""
			idx = 0
			while True:
				curidx = detailcont[idx:].find(flag)
				if curidx < 0:
					break
				idx = idx + curidx
				idx += len(flag)
				curidx = detailcont[idx:].find(">")
				if curidx < 0:
					break
				start = idx + curidx
				start += 1
				curidx = detailcont[start:].find("</a>")
				if curidx < 0:
					break
				end = start + curidx
				idx = end + 1
				curclassfy = detailcont[start:end]
				curclassfy = curclassfy.strip().strip("\t")
				if len(curclassfy) == 0:
					continue
				#print "curclassfy", curclassfy
				classfy.append(curclassfy)
				if len(classfystr) > 0:
					classfystr += " "
				classfystr += curclassfy
				#做统计
				key = "%s\t%d" % (curclassfy, mediatype)
				try:
					ret[key][0] += pv
					ret[key][1] += praisenum
					ret[key][2] += replycount
					ret[key][3] += 1
				except:
					ret[key] = [pv, praisenum, replycount, 1]
			if len(classfy) == 0:
				common.LogErr("%s: null platformlabel:" % detailurl)
				continue
			count += 1
			print "%d\turl:%s\tmediatype:%d\tpv:%d\tpraisenum:%d\treplycount:%d\tclassfy:%s" % (count, detailurl, mediatype, pv, praisenum, replycount, classfystr) 
	except:
		traceback.print_exc()
	time.sleep(FETCH_INTERVAL)

print "\n\n===========================统计结果==========================="
print "分类标签\t内容形式\t平均阅读数/平均播放数\t平均点赞数\t平均评论数"
#输出统计结果
for k in ret:
	classfy, mediatype = k.split("\t")
	classfy = classfy
	mediatype = int(mediatype)
	mediatypestr = ""
	if mediatype == 1:
		mediatypestr = "长文"
	if mediatype == 2:
		mediatypestr = "轻文"
	if mediatype == 3:
		mediatypestr = "视频"
	print "%s\t%s\t%d\t%d\t%d" % (classfy, mediatypestr, int(round(ret[k][0] / float(ret[k][3]))), int(round(ret[k][1] / float(ret[k][3]))), int(round(ret[k][2] / float(ret[k][3]))))
