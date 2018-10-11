# -*- encoding: utf-8 -*-
import re
from datetime import datetime
from collections import defaultdict
from urllib.parse import urlparse

def add_to_url_dict(slow_dict, url_dict, line, ignore_files, ignore_urls, request_type, ignore_www, slow_queries):
    
    time_req = int(line[6])
    
    if request_type:
        if not request_type == line[2][1:]:
            return False
    
    if ignore_urls:
        for url in ignore_urls:
            if url in line[3]:
                return False
        
    if ignore_www:
        if 'www' in line[3]:
            line[3] = line[3].replace('www.', '')
            
    line = urlparse(line[3])
    
    if slow_queries:
        slow_dict[line.netloc + line.path] += time_req
    
    if ignore_files:
        if re.search('\.\w{2}', line.path):
            return False
    
    url_dict[line.netloc + line.path] += 1

    return url_dict

def create_top_five_url(url_dict):
    my_list = sorted(url_dict, key = url_dict.get, reverse = True)
    my_list = my_list[:5]
    for k in range(len(my_list)):
        my_list[k] = url_dict.get(my_list[k])
    return my_list

def create_untop_five_url(url_dict, slow_dict):
    my_list1 = sorted(slow_dict, key = slow_dict.get, reverse = True)
    for k in range(len(my_list1)):
        my_list1[k] = slow_dict.get(my_list1[k]) // url_dict.get(my_list1[k])
    my_list1.sort(reverse = True)
    my_list1 = my_list1[:5]
    return my_list1

def parse(
    ignore_files=False,
    ignore_urls=[],
    start_at=None,
    stop_at=None,
    request_type=None,
    ignore_www=False,
    slow_queries=False
):
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
                if start_at and stop_at:
                    if start_at < date < stop_at:
                        add_to_url_dict(slow_dict, url_dict, line, ignore_files, ignore_urls, request_type, ignore_www, slow_queries)
                elif start_at:
                    if start_at < date:
                        add_to_url_dict(slow_dict, url_dict, line, ignore_files, ignore_urls, request_type, ignore_www, slow_queries)
                else:
                    if date < stop_at:
                        add_to_url_dict(slow_dict, url_dict, line, ignore_files, ignore_urls, request_type, ignore_www, slow_queries)
            else:
                add_to_url_dict(slow_dict, url_dict, line, ignore_files, ignore_urls, request_type, ignore_www, slow_queries)
    if slow_queries:
        return create_untop_five_url(url_dict, slow_dict)
    else:
        return create_top_five_url(url_dict)

parse()
