# -*- coding:utf-8 -*-


import gc
import numpy as np

from gensim import corpora, models, similarities
from sentence import Sentence
from collections import defaultdict


class SentenceSimilarity():

    def __init__(self,seg):
        self.seg = seg

    def set_sentences(self,sentences):
        self.sentences = []

        for i in range(0,len(sentences)):
            self.sentences.append(Sentence(sentences[i],self.seg,i))

    # 获取切过词的句子
    def get_cuted_sentences(self):
        cuted_sentences = []

        for sentence in self.sentences:
            cuted_sentences.append(sentence.get_cuted_sentence())

        return cuted_sentences

    # 构建其他复杂模型前需要的简单模型
    def simple_model(self,min_frequency = 1):
        self.texts = self.get_cuted_sentences()

        # 删除低频词
        frequency = defaultdict(int)
        for text in self.texts:
            for token in text:
                frequency[token] += 1

        self.texts = [[token for token in text if frequency[token] > min_frequency] for text in self.texts]
        print '%d words colleted from training corpus' % len(self.texts)
        self.dictionary = corpora.Dictionary(self.texts)
        self.corpus_simple = [self.dictionary.doc2bow(text) for text in self.texts]

    # tfidf模型
    def TfidfModel(self):
        self.simple_model()

        # 转换模型
        self.model = models.TfidfModel(self.corpus_simple)
        self.corpus = self.model[self.corpus_simple]

        # 创建相似度矩阵
        self.index = similarities.MatrixSimilarity(self.corpus)

    # lsi模型
    def LsiModel(self):
        self.simple_model()

        # 转换模型
        self.model = models.LsiModel(self.corpus_simple)
        self.corpus = self.model[self.corpus_simple]

        # 创建相似度矩阵
        self.index = similarities.MatrixSimilarity(self.corpus)

    #lda模型
    def LdaModel(self):
        self.simple_model()

        # 转换模型
        self.model = models.LdaModel(self.corpus_simple)
        self.corpus = self.model[self.corpus_simple]

        # 创建相似度矩阵
        self.index = similarities.MatrixSimilarity(self.corpus)

    def sentence2vec(self,sentence):
        sentence = Sentence(sentence,self.seg)
        vec_bow = self.dictionary.doc2bow(sentence.get_cuted_sentence())
        return self.model[vec_bow]

    # 求最相似的句子
    def similarity(self,sentence):
        sentence_vec = self.sentence2vec(sentence)

        sims = self.index[sentence_vec]
        sim = max(enumerate(sims), key=lambda item: item[1])

        index = sim[0]
        score = sim[1]
        sentence = self.sentences[index]

        sentence.set_score(score)
        return sentence

    # get top-K similar sentence
    def similarityK(self,sentence, topK=5):
        sentence_vec = self.sentence2vec(sentence)

        sims = self.index[sentence_vec]

        sims_np = np.asarray(sims)

        idx_sort = np.argsort(-sims_np)

        sentenceK = []

        for i in range(topK):
            sentence_i = self.sentences[idx_sort[i]]
            sentence_i.set_score(sims_np[idx_sort[i]])
            sentence_i.id = idx_sort[i]

            sentenceK.append(sentence_i)

        return sentenceK


