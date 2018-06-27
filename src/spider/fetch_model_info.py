#!/usr/bin/python
# -*- coding: utf-8 -*- 

# 获取车型信息
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

# 获取车型信息： 汽车之家车型ID 车型名车 车型年代  汽车之家车系ID 
def get_model_list(chexiId):

    #要返回的数据
    model_list = []

    send_headers = {
        "User-Agent": USER_AGENT,
        "Connection": "Keep-Alive",
        #"Accept-Encoding": "gzip",
    }

    preurl = "https://cars.app.autohome.com.cn/carinfo_v8.9.5/cars/seriessummary-pm2-s%s-t-c110100-v9.0.5.json"
    url = preurl % (chexiId)
    try:
        req = urllib2.Request(url, headers=send_headers)
        cont = urllib2.urlopen(req).read()
        mp = json.loads(cont)

        enginelist = mp['result']['enginelist']
        for item in enginelist:
            if item['yearname'] == '全部在售': 
                # 只统计各个年限下的车型就行
                continue
            else: 
                for yearspec in item['yearspeclist']:
                    # if yearspec['name'] == '参数配置未公布':
                    #     continue
                    for spec in yearspec['speclist']:

                        saleState = spec['state']
                        if saleState == 0:
                            saleState = '未售'
                        elif saleState == 20:
                            saleState = '在售'
                        elif  saleState == 40:
                            saleState = '停售'
                        else:
                            saleState = '销售状态未知'

                        model_item = {
                            'id': spec['id'],
                            'name' : spec['name'],
                            'year' : item['yearname'].replace('款',''),
                            'chexiId' : chexiId,
                            'saleState': saleState,
                        }
                        
                        model_list.append(model_item)                    
    except:
        traceback.print_exc()

    return model_list


chexiFile = sys.argv[1]
chexiIdList = get_chexi_from_outerfile(chexiFile)

print "汽车之家车型ID\t车型名称\t车型年代\t汽车之家车系id\t车型销售状态"
for chexiId in chexiIdList:
    # 循环抓取车型列表
    model_list = get_model_list(chexiId)

    #输出
    for model in model_list:
        sys.stdout.write("%s\t%s\t%s\t%s\t%s\n" % (model['id'], model['name'], model['year'],model['chexiId'],model['saleState']))

    #sleep 1秒
    time.sleep(FETCH_INTERVAL)
    break;
    

    
