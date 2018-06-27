#!/usr/bin/python
# -*- coding: utf-8 -*- 
import common, urllib2, json, traceback, time, utils, socket, sys

reload(sys)
sys.setdefaultencoding('utf-8') 
socket.setdefaulttimeout(5.0)

USER_AGENT  = "Android\t7.0\tautohome\t8.7.0\tAndroid"
FETCH_INTERVAL = 1

# 根据生产厂商属性拉取车系
def get_chexi_list(fctattr):
    
    url_base = "https://cars.app.autohome.com.cn/cars_v8.8.5/cars/searchcars.ashx?pm=2&pluginversion=9.0.5&minp=0&maxp=0&levels=&cids=&gs=&sts=&dsc=&configs=&order=2&pindex=%s&psize=%s&bids=&fids=&drives=&seats=&attribute=%s&flowmode=&tags=&mileage="
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
            url = url_base % (pindex, psize, fctattr)
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

def print_chexi_fctattr(chexiIdList, fctattr):
    if len(chexiIdList) <= 0:
        return

    #厂商属性参数： 1 自主;  2 合资; 3 进口;
    if fctattr == 1:
        fctattr = '自主'
    elif fctattr == 2:
        fctattr = '合资'
    elif fctattr == 3:
        fctattr = '进口'
    else:
        fctattr = '未知'

    for chexiId in chexiIdList:
        #输出车系id和国别
        sys.stdout.write("%s\t%s\n" % (chexiId,fctattr))

    return





#主流程
fctattrs = [1,2,3]
for fctattr in fctattrs:
    # 循环抓取车系信息
    chexiIdList = get_chexi_list(fctattr)
    #输出车系id和厂商属性
    print_chexi_fctattr(chexiIdList, fctattr)
    
    break

    
