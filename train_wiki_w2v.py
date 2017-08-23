#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys
import multiprocessing
import gensim  

reload(sys)
sys.setdefaultencoding('utf-8')


def word2vec_train(input_file, output_file):
    sentences = gensim.models.word2vec.LineSentence(input_file)
    model = gensim.models.Word2Vec(sentences, size=300, min_count=10, sg=0, workers=multiprocessing.cpu_count())
    model.save(output_file)
    model.ww.save_word2vec_format(output_file + '.vector', binary=True)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "Usage: python script.py infile outfile"
        sys.exit()
    input_file, output_file = sys.argv[1], sys.argv[2]
    word2vec_train(input_file, output_file)
