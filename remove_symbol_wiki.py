#!/usr/bin/python
# -*- coding: utf-8 -*- 

import sys
import re
import io

reload(sys)
sys.setdefaultencoding('utf-8')

def pre_process(input_file, output_file):
    multi_version = re.compile(ur'-\{.*?(zh-hans|zh-cn):([^;]*?)(;.*?)?\}-')
    punctuation = re.compile(u"[-~!@#$%^&*()_+`=\[\]\\\{\}\"|;':,./<>?·！@#￥%……&*（）——+【】、；‘：“”，。、《》？「『」』]")
    with io.open(output_file, mode = 'w', encoding = 'utf-8') as outfile:
        with io.open(input_file, mode = 'r', encoding ='utf-8') as infile:
            for line in infile:
                line = multi_version.sub(ur'\2', line)
                line = punctuation.sub('', line.decode('utf8'))
                outfile.write(line)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print "Usage: python script.py input_file output_file"
        sys.exit()
    input_file, output_file = sys.argv[1], sys.argv[2]
    pre_process(input_file, output_file)
