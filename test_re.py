# -*- coding: utf-8 -*-
import re

s = '<a href="http://jzb.com/bbs/bj/" onclick="javascript:gotourl(\'bj\');" class=\'bj\'>上海</a>'
p_city = s.find('上海')
print p_city
