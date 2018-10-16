# -*- encoding: utf-8 -*-
import re
from datetime import datetime
from collections import defaultdict
from urllib.parse import urlparse

def add_to_url_dict(slow_dict, url_dict, line, ignore_files, ignore_urls, request_type, ignore_www, slow_queries):
    
    time_req = int(line[6])
    
    if request_type:
        if not request_type == line[2][1:]:
            return
    
    line = urlparse(line[3])

    if ignore_urls and line.netloc + line.path in ignore_urls:
        return

    if ignore_files:
        if re.search('\.\w{2}', line.path):
            return 

    if slow_queries:
        slow_dict[line.netloc + line.path] += time_req

    if ignore_www and line.netloc.rfind('www.', 0, 4) == 0:
        url_dict[re.sub('www.', '', line.netloc, 1) + line.path] += 1
    else:
        url_dict[line.netloc + line.path] += 1
        
    return url_dict

def create_top_five_url(url_dict):
    my_list = sorted(url_dict, key = url_dict.get, reverse = True)
    my_list = my_list[:5]
    for k in range(len(my_list)):
        my_list[k] = url_dict.get(my_list[k])
    return my_list

def create_untop_five_url(url_dict, slow_dict):
    my_list = []
    for key in url_dict:
        time = slow_dict.get(key) // url_dict.get(key)
        my_list.append(time)
    my_list.sort(reverse = True)
    return my_list[:5]

def parse(
    ignore_files=False,
    ignore_urls=[],
    start_at=None,
    stop_at=None,
    request_type=None,
    ignore_www=False,
    slow_queries=False
):
    if ignore_urls:
        ignore_urls = set(ignore_urls)
    if start_at:
        start_at = datetime.strptime(start_at, '%d/%b/%Y %X')
    if stop_at:
        stop_at = datetime.strptime(stop_at, '%d/%b/%Y %X')
    url_dict = defaultdict(int)
    slow_dict = defaultdict(int)
    log = open('log.log')
    for line in log:
        if re.search('\d\d/\w{3}/\d{4}', line):
            line = line.split()
            if start_at or stop_at:
                date = "{} {}".format(line[0][1:], line[1][:-1])
                date = datetime.strptime(date, '%d/%b/%Y %X')
                if (not start_at or start_at < date) and (not stop_at or stop_at > date):
                    add_to_url_dict(slow_dict, url_dict, line, ignore_files, ignore_urls, request_type, ignore_www, slow_queries)
            else:
                add_to_url_dict(slow_dict, url_dict, line, ignore_files, ignore_urls, request_type, ignore_www, slow_queries)
    if slow_queries:
        return create_untop_five_url(url_dict, slow_dict)
    else:
        return create_top_five_url(url_dict)

parse()
