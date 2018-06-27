#!/usr/bin/python
# -*- coding: utf-8 -*- 
import common, urllib2, json, traceback, time, utils, socket, sys

reload(sys)
sys.setdefaultencoding('utf-8') 
socket.setdefaulttimeout(5.0)

USER_AGENT  = "Android\t7.0\tautohome\t8.7.0\tAndroid"

FETCH_INTERVAL = 0.3 

# 抓取汽车之家所有品牌id与品牌名称
def get_brand_from_outerfile(file_name):
    brandIdList = []

    i = 1
    for line in open(file_name).readlines():
        line = line.strip("\n")
        cols = line.split("\t")
        try:
            if cols[0].isdigit():
                brandIdList.append(cols[0])
        except:
            traceback.print_exc()

    return brandIdList

def get_chexi_info(brandId):
    #https://cars.app.autohome.com.cn/cars_v8.8.5/cars/seriesprice-pm2-b14-t16-v9.0.5-c110100.json?pluginversion=9.0.5
    preurl = "https://cars.app.autohome.com.cn/cars_v8.8.5/cars/seriesprice-pm2-b";
    tailurl = "-t16-v9.0.5-c110100.json?pluginversion=9.0.5";
    url = preurl + brandId + tailurl;

    send_headers = {
        "User-Agent": USER_AGENT,
        "Connection": "Keep-Alive",
        #"Accept-Encoding": "gzip",
    }

    try:
        req = urllib2.Request(url, headers=send_headers)
        cont = urllib2.urlopen(req).read()
        mp = json.loads(cont)
        #厂商列表
        allFctList = []
        for fct in mp['result']['fctlist']:
            allFctList.append(fct)
        for fct in mp['result']['otherfctlist']:    
            allFctList.append(fct)

        for fct in allFctList:
            #厂商名称
            fctName = fct['name']

            for chexi in fct['serieslist']:
                chexiId    = chexi["id"]
                chexiName  = chexi['name']
                chexiLevel = chexi['levelname']
                chexiPrice = chexi['price']
                chexiState = chexi['state']
                if chexiState == 0:
                    chexiState = '未售'
                elif chexiState == 20:
                    chexiState = '在售'
                elif  chexiState == 40:
                    chexiState = '停售'
                else:
                    chexiState = '销售状态未知'

                # 获取车系下在售车型百公里油耗最大值和最小值
                chexiFuelStat = get_gxb_fuel_stat(chexiId)
                chexiFuelMax = chexiFuelStat['max']
                chexiFuelMin = chexiFuelStat['min']

                sys.stdout.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (chexiId, brandId, chexiName, chexiLevel,chexiPrice, fctName, chexiState, chexiFuelMax, chexiFuelMin))
                #break
    except:
        traceback.print_exc()


def get_gxb_fuel_stat(brandId):

    #返回数据结构
    fuel_stat = {
        "max":0,
        "min":0
    }

    send_headers = {
        "User-Agent": USER_AGENT,
        "Connection": "Keep-Alive",
        #"Accept-Encoding": "gzip",
    }

    #获取在售车型ids
    model_ids = []

    preurl = "https://cars.app.autohome.com.cn/carinfo_v8.9.5/cars/seriessummary-pm2-s%s-t-c110100-v9.0.5.json"
    url = preurl % (brandId)
    try:
        req = urllib2.Request(url, headers=send_headers)
        cont = urllib2.urlopen(req).read()
        mp = json.loads(cont)

        enginelist = mp['result']['enginelist']
        for item in enginelist:
            if item['yearname'] == '全部在售': 
                for yearspec in item['yearspeclist']:
                    if yearspec['name'] == '参数配置未公布':
                        continue

                    for spec in yearspec['speclist']:
                        model_ids.append(str(spec['id'])) 
    except:
        traceback.print_exc()

    # 车系对应在售车型为空,则直接返回空
    if len(model_ids) <= 0:
        return fuel_stat

    # 获取车型ids对应的百公里油耗信息
    fuel_values = []
    preurl = "https://cars.app.autohome.com.cn/cfg_v8.5.0/cars/speccompare.ashx?pluginversion=9.0.0&type=1&specids=%s&cityid=110100&site=1&pl=2"
    str_model_ids = ','.join(model_ids)
    url = preurl % str_model_ids
    
    try:
        req = urllib2.Request(url, headers=send_headers)
        cont = urllib2.urlopen(req).read()
        mp = json.loads(cont)

        paramitems = mp['result']['paramitems']
        for param in paramitems:
            items = param['items']
            # 工信部综合油耗
            for item in items:
                if item['id'] == '271': 
                    for one in item['modelexcessids']:
                        value = str(one['value']).replace('u','')
                        if value == '-':
                            continue
                        else:
                            value = float(value)
                            
                        fuel_values.append(value)
    except:
        traceback.print_exc()

 
    # 范围车系在售车型百公里油耗最大值和最小值

    if len(fuel_values) <= 0:
        fuel_stat = {
            "max":0,
            "min":0
        }
    else:
        fuel_stat = {
            "max": max(fuel_values),
            "min": min(fuel_values)
        }

    return fuel_stat


brandFile = sys.argv[1]
brandIdList = get_brand_from_outerfile(brandFile)


print "车系ID\t品牌ID\t车系名\t车系级别\t车系厂商指导价\t厂商\t车系销售状态\t车系工信部油耗最大值\t工信部油耗最低值\n"
for brandId in brandIdList:
    #brandId = '279'
    # 循环抓取车系信息
    get_chexi_info(brandId)

    #sleep 1秒
    time.sleep(FETCH_INTERVAL)
    break;
    

    
