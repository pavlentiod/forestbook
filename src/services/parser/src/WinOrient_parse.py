# -*- coding: utf-8 -*-
import re

import pandas as pd
from bs4 import BeautifulSoup as BS
from pandas import Timedelta

from src.services.parser.src.utils import points_to_routes, fill_GD, dispersions, null, bs

global log


def check_type(line):
    l = len(re.findall('\d{2}:\d{2}:\d{2}\(', line))
    if l != 0:
        # print(1)
        check = 1
    elif l == 0:
        # print(2)
        r = re.findall('\s\d{1,2}:\d{2}\(', line)
        r_l = len(r)
        r1 = [i for i in re.findall('\(\d{1,2}\)', line.replace(' ', '')) if int(i[1:-1]) < 10]
        r2 = re.findall('\(\d{2}\)\(', line.replace(' ', ''))
        r1_l = len(r1)
        r2_l = len(r2)
        if (r_l != 0) & (r1_l != 0) & (r2_l != 0):
            check = 3
        elif (r_l != 0) & (r1_l != 0):
            # print(3)
            check = 0
        elif (r_l != 0) & (r1_l == 0):
            # print(4, r2, l2)
            check = 3
        else:
            print(r_l, r1_l, r2_l)
            check = 2
    return check


def check_time(splits, result):
    l = [i if i < result else pd.NaT for i in splits]
    l[-1] = pd.NaT if l.count(pd.NaT) != 0 else l[-1]
    return l


def extract_points(line):  # TAKE ALL BRACKETS LIKE (34)(78)
    reg = ':\d{2}\(\d+\)'
    s = line.replace(' ', '')
    points = ['241'] + [i[4:-1] for i in re.findall(reg, s)] + ['240']
    return points_to_routes(points)


def extract_points_2(soup):
    b = bs(soup).find('b').text.replace(' ', '')
    reg = '\(\d{2,3}\)'
    points = ['241'] + [i[1:-1] for i in re.findall(reg, b)] + ['240']
    return points_to_routes(points)


def extract_points_3(soup, group_name, split_count):
    b = bs(soup).find('b').text.replace(' ', '')
    reg = '\(\d{2,3}\)'
    points = [i[1:-1] for i in re.findall(reg, b)]
    if len(points) + 1 != split_count:
        points = ['241'] + [f'{i}_{group_name}' for i in list(range(1, split_count))] + ['240']
    return points_to_routes(points)


def extract_name(line):
    s = ' '.join(line.split())
    return ' '.join([i.strip() for i in re.findall('\s\w+', s)[:2]]).upper()


def extract_time_data(line):
    s = ' '.join(line.split())
    return [Timedelta(i[:-1]) for i in re.findall('\d{2}:\d{2}:\d{2}\(', s)]


def extract_result(line):
    try:
        result = re.findall('\d{2}:\d{2}:\d{2}\s', ' '.join(line.split()))[0].strip()
    except:
        result = Timedelta(hours=100)
    return Timedelta(result)


def extract_splits(line, result):
    time_data = extract_time_data(line)
    splits = time_data + [result - pd.Series(time_data, dtype='timedelta64[ns]').sum()]
    return check_time(splits, result)


def extract_splits_2(line, result):
    reg = re.findall('\d{1,2}:\d{2}\(', line)
    l = [Timedelta(minutes=int(i.split(':')[0]), seconds=int(i.split(':')[1][:-1])) for i in reg]
    l = l + [result - pd.Series(l, dtype='timedelta64[ns]').sum()]
    return check_time(l, result)


def extract_splits_3(line, result):
    reg = re.findall('\s\d+:\d{2}\s', line.replace(' ', '  '))
    l = [Timedelta(minutes=int(i.split(':')[0][1:]), seconds=int(i.split(':')[1][:-1])) for i in reg][:]
    sum = pd.Series(l, dtype='timedelta64[ns]').sum()
    l = l + [result - sum]
    return check_time(l, result)


def groups_data(page):
    reg = r'\S+\b'
    h2 = [re.findall(reg, i.get_text(' '))[0] for i in page.find_all('h2')]
    groups = page.find_all('pre')
    return h2, groups


def group_frame(group: str, soup: BS):
    names, points_l, splits_l, results = group_general_data(soup, group)
    # print(names)
    print(points_l)
    # print(splits_l)
    # print(results)
    GD = fill_GD(names, points_l, splits_l, results)
    disps = dispersions(points_l)
    df = pd.DataFrame(GD, dtype='timedelta64[ns]').T
    return df, disps


def group_general_data(group_data, group_name):
    group_l = [i for i in str(group_data).splitlines()[1:-1] if 'u>' not in i]
    res, spl, pnt = {}, {}, {}
    names = []
    check = check_type(group_l[0])
    for line in group_l[:]:
        try:
            name = extract_name(line) + '^' + group_name.upper()
            result = extract_result(line)
            if check == 1:
                splits = extract_splits(line, result)
                points = extract_points(line)
            elif check == 0:
                splits = extract_splits_2(line, result)
                points = extract_points_2(group_data)
            elif check == 2:
                splits = extract_splits_3(line, result)
                points = extract_points_3(group_data, group_name, len(splits))
            # elif check == 3:
            else:
                splits = extract_splits_2(line, result)
                points = extract_points(line)

            pnt.setdefault(name, points)
            res.setdefault(name, result)
            spl.setdefault(name, splits)
            names.append(name)
        except Exception as e:
            print(e)

    return names, pnt, spl, res


def SI_parsing(soup):
    global log
    log = 'group frame error'
    df = pd.DataFrame()
    routes = {}
    h2, soups = groups_data(soup)
    group_pack = list(zip(h2[:], soups[:]))
    for group_name, group_soup in group_pack[:]:
        try:
            group_df, disps = group_frame(group_name, group_soup)
        except Exception as e:
            continue
        df = pd.concat([df, group_df], join='outer', axis=0)
        routes.setdefault(group_name.upper(), disps)
    log = 'correct'
    if df.shape[1] < 3:
        log = 'only res'
    df = df.replace([null], pd.NaT)
    df.index.name = 'name'
    return df, routes
