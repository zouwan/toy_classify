#!/usr/bin/python
# -*- coding: utf-8 -*- 
import common, urllib2, json, traceback, time, utils, socket, sys

reload(sys)
sys.setdefaultencoding('utf-8') 
socket.setdefaulttimeout(5.0)

USER_AGENT  = "Android\t7.0\tautohome\t8.7.0\tAndroid"
FETCH_INTERVAL = 1

# 根据国别cid拉取所属车系列表
def get_chexi_list(cid):
    
    url_base = "https://cars.app.autohome.com.cn/cars_v8.8.5/cars/searchcars.ashx?pm=2&pluginversion=9.0.5&minp=0&maxp=0&levels=&cids=%s&gs=&sts=&dsc=&configs=&order=2&pindex=%s&psize=%s&bids=&fids=&drives=&seats=&attribute=0&flowmode=&tags=&mileage="
    send_headers = {
        "User-Agent": USER_AGENT,
        "Connection": "Keep-Alive",
        #"Accept-Encoding": "gzip",
    }

    try:
        chexiIdList = []

        pindex = 1
        psize  = 20
        while (1):
            url = url_base % (cid,pindex,psize)
            req = urllib2.Request(url, headers=send_headers)
            cont = urllib2.urlopen(req).read()
            mp = json.loads(cont)

            seriesitems = mp['result']['seriesitems']

            for series in seriesitems:
                #车系id
                chexiId = series['id']
                chexiIdList.append(chexiId)

            if len(seriesitems) < psize:
                break

            #拉取下一页
            pindex += 1
            #暂停1秒,别把人家网站抓挂了
            time.sleep(FETCH_INTERVAL)

    except:
        traceback.print_exc()

    return chexiIdList

def print_chexi_guobie(chexiIdList, cid):
    if len(chexiIdList) <= 0:
        return

    #国别参数： 1 中国; 2 德国; 3 日本; 4 美国; 5 韩国; 6 法国; 7 英国; 13 其他 ; 0 未知
    if cid == 1:
        cid = '中国'
    elif cid == 2:
        cid = '德国'
    elif cid == 3:
        cid = '日本'
    elif cid == 4:
        cid = '美国'
    elif cid == 5:
        cid = '韩国'
    elif cid == 6:
        cid = '法国'
    elif cid == 7:
        cid = '英国'
    elif cid == 13:
        cid = '其他'
    else:
        cid = '未知'

    for chexiId in chexiIdList:
        #输出车系id和国别
        sys.stdout.write("%s\t%s\n" % (chexiId,cid))

    return





#主流程
cids = [1,2,3,4,5,6,7,13]
for cid in cids:
    # 循环抓取车系信息
    chexiIdList = get_chexi_list(cid)
    #输出车系id和国别
    print_chexi_guobie(chexiIdList, cid)
    
    break

    
