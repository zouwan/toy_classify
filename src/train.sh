#!/bin/bash

# raw data path
raw=../data/out/sample

# binary classification cat
cat=$1
test_rate=0.1

TMP=../data/tmp
mkdir -p $TMP

echo "cat ${raw}* | grep __label__$cat | awk -F\"\t\" '{print $1\"\t__label__1\"}' > $TMP/pos_$cat"
cat ${raw}* | grep __label__$cat | awk -F"\t" '{print $1"\t__label__1"}' | shuf > $TMP/pos_$cat

pos_num=`wc -l $TMP/pos_$cat| awk '{print $1}'`; echo "pos_num=$pos_num"
pos_train_num=`echo "$pos_num * (1-$test_rate)"| bc | awk -F"." '{print $1}'`; echo "pos_train_num=$pos_train_num"
pos_test_num=`echo "$pos_num * $test_rate"|bc| awk -F"\." '{print $1}'`; echo "pos_test_num=$pos_test_num"
head -n $pos_train_num $TMP/pos_$cat > $TMP/train_pos_$cat
tail -n $pos_test_num $TMP/pos_$cat > $TMP/test_pos_$cat

echo "cat ${raw}* | grep -v __label__$cat | awk -F\"\t\" '{print $1\"\t__label__0\"}' > $TMP/neg_$cat"
cat ${raw}* | grep -v __label__$cat | awk -F"\t" '{print $1"\t__label__0"}' | shuf> $TMP/neg_$cat
neg_num=`wc -l $TMP/neg_$cat| awk '{print $1}'`; echo "neg_num=$neg_num"
neg_train_num=`echo "$neg_num * (1-$test_rate)"|bc | awk -F"." '{print $1}'`; echo "neg_train_num=$neg_train_num"
neg_test_num=`echo "$neg_num * $test_rate"|bc| awk -F"." '{print $1}'`; echo "neg_test_num=$neg_test_num"
head -n $neg_train_num $TMP/neg_$cat > $TMP/train_neg_$cat
tail -n $neg_test_num $TMP/neg_$cat > $TMP/test_neg_$cat

cat $TMP/train_neg_$cat $TMP/train_pos_$cat > $TMP/train_$cat
cat $TMP/test_neg_$cat $TMP/test_pos_$cat > $TMP/test_$cat

#FASTTEXT="../../../fastText/fasttext"
#$FASTTEXT supervised -input $TMP/train_$cat -output data/model_$cat -epoch 25 -wordNgrams 2
#$FASTTEXT test data/model_${cat}.bin $TMP/test_$cat 

python train.py $cat ../data/model_$cat
