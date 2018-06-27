# -*- coding: utf-8 -*-
#  code by zach. zouwan@gmail.com
#  sample data process.
#    1. 标签对应样本聚合
#    2. 生成训练样本和测试样本 shuju
#    3. 原始数据: 汽车之家口碑数据， koubei_tag, koubei_tag_comment
import sys
import glob
import json
import os.path
import jieba
import re
import multiprocessing
reload(sys)
sys.setdefaultencoding('utf8')

html_tag = "<img /><a>srcd</a>hello</br><br/>"

ROOT_PATH="../"
OUTPATH=ROOT_PATH + "data/out/" 
try:
    os.makedirs(OUTPATH)
except:
    pass
PRO_NUM = 48 # 结巴分词较慢，mac pro用多进程大概2个小时
KOUBEI_TAG=ROOT_PATH + "data/koubei_tag/"
KOUBEI_TAG_COMMENT=ROOT_PATH + "data/koubei_tag_comment/"
KOUBEI_ID_TAGS = ROOT_PATH + "data/id_tags"
STOP_WORD_PATH=ROOT_PATH + "data/stop_words.txt"

tagDict = {}
tagDictMap = {}
stopWords = []

#获取停用词表
def get_stopwords(path):
    f= open(path)
    stopwords=[]
    for line in f:
        stopwords.append(line.strip().decode("utf-8").encode("utf-8"))
    return stopwords


def load_tag_mapping(path):
    # 1. load tag
    for filename in glob.glob(KOUBEI_TAG + "*.json"):
        car_type = os.path.basename(filename).split('.')[0]
        try:
            with open(filename, 'r+') as fd:
                obj = json.load(fd)
                for ob in obj:
                    for ob1 in ob["Summary"]:
                        if str(ob1["Combination"]) not in tagDict:
                            tagDict[str(ob1["Combination"])] = set()
                        tagDict[str(ob1["Combination"])].add(str(ob1["SummaryKey"]))
        except:
            pass

    with open(KOUBEI_ID_TAGS, 'r+') as fd:
        lines = fd.readlines()
        for line in lines:
            items = line.split(" ")
            i = 1
            while i < len(items):
                if items[i] in tagDict:
                    for x in tagDict[items[i]]:
                        tagDictMap[x] = items[0]
                i+=1

##去除标点符号
def remove_punctuation(line):
    #中文标点 ！？｡＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､、〃》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘’‛“”„‟…‧﹏.
    #英文标点 !"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~
    try:
      line = re.sub("[！？？。｡＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､、〃《》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘’‛“”„‟…‧﹏.!\"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~]+".decode("utf-8"), "",line.decode("utf-8"))
    except Exception as e:
      print "error"
    return line



def generate_data(procid, flist):
    with open(OUTPATH + "sample_" + str(procid), 'w+') as wd:
        i = 0
        fnum = len(flist)
        for filename in flist:
            print str(procid) + ": " + str(i) + "/" + str(fnum) + " " + filename
            i+=1
            koubei_type = filename.split('-')[1]
            with open(filename, 'r+') as fd:
                obj = json.load(fd)
                for ob in obj:
                    line = re.sub(r'</?\w+[^>]*>','', ob["contents"][0]["content"])
                    final=[]
                    seg_list = jieba.cut(remove_punctuation(line.decode("utf-8").encode("utf-8")).replace("\n", " ").replace("\t", " "))
                    for seg in seg_list:
                        if seg not in stopWords:
                            final.append(seg)
                    wd.write(u" ".join(final) + u"\t__label__" + str(tagDictMap[str(koubei_type)]) + "\n")


if __name__ == "__main__":
    # load tag mapping
    #  @fengwei 找同学人工做了同类标签聚合
    load_tag_mapping(KOUBEI_ID_TAGS)

    # stopword
    stopWords=get_stopwords(STOP_WORD_PATH)

    i = 0
    file_list = {}
    for filename in glob.glob(KOUBEI_TAG_COMMENT + "*.json"):
        koubei_typ = filename.split('-')[1]
        if koubei_typ not in tagDictMap:
            continue
        if i not in file_list:
            file_list[i] = []
        file_list[i].append(filename)
        i = (i + 1) % PRO_NUM

    # gen data
    jobs = []
    for i in range(PRO_NUM):
        print i
        p = multiprocessing.Process(target=generate_data, args=(i, file_list[i]))
        jobs.append(p)
        p.start()
    for i in jobs:
        i.join()
