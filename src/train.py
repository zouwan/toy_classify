#-*- coding:utf8 -*-
import logging
import fasttext
import sys
from fastText import train_supervised

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

cat=sys.argv[1]
train_data_path="../data/tmp/train_"+cat
test_data_path="../data/tmp/test_"+cat
output_model_path=sys.argv[2]


def print_results(n, p, r):
    print("N\t" + str(n))
    print("P@{}\t{:.3f}".format(1, p))
    print("R@{}\t{:.3f}".format(1, r))


def print_result_by_cat(model):
    labels_right = []
    texts = []
    with open(test_data_path) as fr:
        lines = fr.readlines()
    for line in lines:
        labels_right.append(line.split("\t")[1].rstrip().replace("__label__", ""))
        texts.append(line.split("\t")[0].decode("utf-8"))

    # labels 是预测标签， predict 是对应的概率
    labels, predict = model.predict(texts)  # 预测输出结果为二维形式

    text_labels = set(labels_right)

    aa = dict.fromkeys(text_labels, 0)  # 预测正确的各个类的数目
    bb = dict.fromkeys(text_labels, 0)  # 测试数据集中各个类的数目
    cc = dict.fromkeys(text_labels, 0)  # 预测结果中各个类的数目

    for i in range(0, len(labels_right)):
        pre_key = labels[i][0].replace("__label__", "")
        bb[labels_right[i]] += 1
        cc[pre_key] += 1
        if labels_right[i] == pre_key:
            aa[labels_right[i]] += 1

    # 计算准确率，召回率，F值
    for key in bb:
        p = float(aa[key]) / float(bb[key])
        r = float(aa[key]) / float(cc[key])
        f = p * r * 2 / (p + r)
        print "%s:\tp:%f\t%fr:\t%f" % (key, p, r, f)


if __name__ == "__main__":
    # 训练模型
    model = train_supervised(input=train_data_path, epoch=25, lr=0.1, wordNgrams=5, verbose=2, minCount=1)
    # 保存模型
    model.save_model(output_model_path)
    # 输出训练结果(召回、准确率），但是由于 fasttext 是多分类，所以只有一个整体评估
    print_results(*model.test(test_data_path))

    # 实际二分类，关注的是正例召回,手动实现一个
    print_result_by_cat(model)
