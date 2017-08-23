#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import io
import jieba

reload(sys)
sys.setdefaultencoding('utf-8')


def cut_words(input_file, output_file):
    count = 0
    with io.open(output_file, mode = 'w', encoding = 'utf-8') as outfile:
        with io.open(input_file, mode = 'r', encoding = 'utf-8') as infile:
            for line in infile:
                line = line.strip()
                if len(line) < 1:  # empty line
                    continue
                if line.startswith('doc'): # start or end of a passage
                    if line == 'doc': # end of a passage
                        outfile.write(u'\n')
                        count = count + 1
                        if(count % 1000 == 0):
                            print('%s articles were finished.......' %count)
                    continue
                for word in jieba.cut(line):
                    outfile.write(word + ' ')
    print('%s articles were finished.......' %count)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "Usage: python script.py input_file output_file"
        sys.exit()
    input_file, output_file = sys.argv[1], sys.argv[2]
    cut_words(input_file, output_file)
