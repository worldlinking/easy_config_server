import numpy as np
from simhash import Simhash
import jieba.posseg as pseg
import re
import langid


class SimHaming:
    '''利用64位数，计算海明距离'''

    def haming_distance(self, code_s1, code_s2):
        x = (code_s1 ^ code_s2) & ((1 << 64) - 1)
        ans = 0
        while x:
            ans += 1
            x &= x - 1
        return ans

    '''利用相似度计算方式,计算全文编码相似度'''

    def get_similarity(self, a, b):
        if a > b:
            return b / a
        else:
            return a / b

    '''对全文进行分词,提取全文特征,使用词性将虚词等无关字符去重'''

    def get_features(self, string):
        word_list = [word.word for word in pseg.cut(string) if
                     word.flag[0] not in ['u', 'x', 'w', 'o', 'p', 'c', 'm', 'q']]
        return word_list

    # 英文分词
    def get_English_features(self, s):
        width = 3
        s = s.lower()
        s = re.sub(r'[^\w]+', '', s)
        return [s[i:i + width] for i in range(max(len(s) - width + 1, 1))]

    '''计算两个全文编码的距离'''

    def get_distance(self, code_s1, code_s2):
        return self.haming_distance(code_s1, code_s2)

    '''对全文进行编码'''

    def get_code(self, string, textType=None):
        if textType == '0':
            return Simhash(self.get_features(string)).value
        if textType == '1':
            return Simhash(self.get_English_features(string)).value

    '''计算s1与s2之间的距离'''

    def distance(self, s1, s2):
        code_s1 = self.get_code(s1)
        code_s2 = self.get_code(s2)
        similarity = (100 - self.haming_distance(code_s1, code_s2) * 100 / 64) / 100
        return similarity


def getDuplicate(data, filepath):
    simer = SimHaming()

    zh_flag = 0
    en_flag = 0
    for i in data:
        type = langid.classify(i)[0]
        if type == 'zh':
            zh_flag += 1
        if type == 'en':
            en_flag += 1
    if zh_flag >= en_flag:
        textType = '0'
    else:
        textType = '1'
    count = 0
    code = []
    for i in data:
        code.append(simer.get_code(i, textType))

    data_len = len(data)
    simhash_data = np.zeros((data_len, data_len))
    flag = np.zeros(data_len)

    for i in range(len(data)):
        for j in range(i, len(data)):
            sim = (100 - simer.haming_distance(code[i], code[j]) * 100 / 64) / 100
            simhash_data[i][j] = sim
            if sim >= 0.8 and i != j:
                flag[j] = 1

    print(data[0], data[1])
    with open(filepath, 'w', encoding='utf-8') as f:
        for i in range(len(data)):
            if flag[i] == 0:
                f.write(data[i].strip('\n') + '\n')
                count += 1
    return count
