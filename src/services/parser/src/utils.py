# -*- coding: utf-8 -*-
import re
from typing import Union

from bs4 import BeautifulSoup as BS
from pandas import Timedelta
from pandas._libs import NaTType


def bs(s: BS):
    soup: BS = BS(str(s), 'html.parser')
    return soup


def course(l: list):
    r = range(len(l) - 1)
    f = lambda x: re.sub(r', ', '->', str(x))[1:-1]
    return [f(l[i:i + 2]) for i in r]


null: Union[Timedelta, NaTType, NaTType] = Timedelta(seconds=0)


def points_to_routes(l: list):
    f = lambda x, i: f'{x[i]}->{x[i + 1]}'
    l: list = [f(l, i) for i in range(len(l) - 1)]
    return l


def rl(l: list):
    return range(len(l))





def fill_GD(names, points_l, splits_l, results):
    GD = {}
    for name in names:
        try:
            sportsman_info = routes_and_splits_dict(points_l[name], splits_l[name])
        except ValueError:
            # print(len(points_l[name]),splits_l[name])
            sportsman_info = {}
        sportsman_info.setdefault('RES', results[name])
        GD.setdefault(name, sportsman_info)
    return GD


def routes_and_splits_dict(routes: list, splits: list):
    #     # print(routes)
    if len(routes) == len(splits):
        d: dict = dict(zip(routes, splits))
        return d
    else:
        raise ValueError(f'{len(routes), len(splits)} lenghts arent same')


def dispersions(d: dict):
    disp = {}
    groups = {}
    for key, value in d.items():
        if value not in disp.values():
            disp[f"disp{len(disp) + 1}"] = value
        groups.setdefault(f"group{list(disp.values()).index(value) + 1}", []).append(key)
    keys = [str(i) for i in disp.values()]
    final_dict = dict(zip(keys, groups.values()))
    return final_dict



