#!/usr/bin/python
# -*- coding: utf-8 -*- 

#获取车系图片
import common, urllib2, json, traceback, time, utils, socket, sys

reload(sys)
sys.setdefaultencoding('utf-8') 
socket.setdefaulttimeout(5.0)

USER_AGENT  = "Android\t7.0\tautohome\t8.7.0\tAndroid"
FETCH_INTERVAL = 0.3

# 从车系文件读取车系id
def get_chexi_from_outerfile(file_name):
    chexiIdList = []

    i = 1
    for line in open(file_name).readlines():
        line = line.strip("\n")
        cols = line.split("\t")
        try:
            if cols[0].isdigit():
                chexiIdList.append(cols[0])
        except:
            traceback.print_exc()

    return chexiIdList

# 获取车系下的图片信息
# typeId:  1 外观; 10 中控; 3 座椅; 12 细节; 14 特点;
def get_chexi_pics(chexiId, typeId):

    send_headers = {
        "User-Agent": USER_AGENT,
        "Connection": "Keep-Alive",
        #"Accept-Encoding": "gzip",
    }

    preurl = "https://cars.app.autohome.com.cn/carinfo_v8.9.5/cars/pics-pm2-ss%s-sp0-cg%s-cl0-p%s-s%s-isn0-ft1-v9.0.5.json?pluginversion=9.0.5"

    pindex = 1
    psize  = 10

    try:
        while 1:
            url = preurl % (chexiId, typeId, pindex , psize)
            req = urllib2.Request(url, headers=send_headers)
            cont = urllib2.urlopen(req).read()
            mp = json.loads(cont)

            picList = mp['result']['piclist']
            if len(picList) <= 0:
                break;

            for pic in picList:
                
                #车型id
                modelId = pic['specid']
                #小图片 240*180
                smallPic = pic['smallpic']
                #大图片 500*375 为啥后面带着.webp
                bigPic   = str(pic['bigpic']).replace('.webp', '')
                #高清图片 1920*1440
                highPic  = pic['highpic']

                # 输出
                sys.stdout.write("%s\t%s\t%s\t%s\t%s\t%s\n" % (chexiId, modelId, typeId, smallPic, bigPic, highPic))

            if len(picList) < psize:
                break

            pindex += 1
            #暂停一会儿,别把人家网站抓挂了
            time.sleep(FETCH_INTERVAL)

            # 图片数量太大,先每个位置拉取10条吧
            # TODO
            break
                  
    except:
        traceback.print_exc()

    return 


chexiFile = sys.argv[1]
chexiIdList = get_chexi_from_outerfile(chexiFile)

# 提醒：灌库时将车系id和车型id替换为顺丰车内部ida
print "汽车之家车系ID\t汽车之家车型ID\t图片类型\t小图片\t大图片\t高清图片\n"

#汽车图片类型  1 外观; 10 中控; 3 座椅; 12 细节; 14 特点;
typeIdList = [1,10,3,12,14]

for chexiId in chexiIdList:
    for typeId in typeIdList:
        get_chexi_pics(chexiId, typeId)
        break
    break;
    

    
