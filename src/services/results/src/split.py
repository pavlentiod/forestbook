# -*- coding: utf-8 -*-
import datetime
import re

import pandas as pd
from fuzzywuzzy import process
from pandas.core.frame import DataFrame
from pandas.core.series import Series

from src.schemas.results.results_schema import Results
from src.schemas.split.split_schema import SplitInput

null = pd.Timedelta(seconds=0)

not_found = []


def sort_by_group(df, group):
    names = df.index.to_list()
    groups = set([name.split('^')[-1] for name in names])
    sorted_athletes = {group: [] for group in groups}
    [sorted_athletes[sp.split('^')[-1]].append(sp) for sp in names]
    group_indexes = sorted_athletes[group]
    return df.loc[group_indexes]


def sort_by_sex(df, sex):
    names = df.index.to_list()
    sex_filtering = {'М': [], 'Ж': []}
    sort = [(nd, 'М') if 'М' in nd.split('^')[-1] else (nd, 'Ж') for nd in names]
    [sex_filtering[ft[1]].append(ft[0]) for ft in sort]
    df = df.loc[sex_filtering[sex]]
    return df


def results_filter(df, group='', filt=''):
    sex = 'М' if 'М' in group.upper() else 'Ж'
    try:
        if filt == 'sex':
            s_df = sort_by_sex(df, sex)
            return s_df
        elif filt == 'group':
            return sort_by_group(df, group)
        else:
            return df
    except Exception as e:
        print(e)
        return df


def format(t: pd.Timedelta):
    if t in [pd.NaT, '']:
        return '-'
    if t < null:
        t = abs(null - t)
        sign = '-'
    else:
        sign = ' '
    t = re.search('\d+:\d+:\d+', str(t))
    dt = datetime.datetime.strptime(t.group(), '%H:%M:%S')
    if dt.hour == 0:
        return sign + dt.strftime('%M:%S')
    else:
        return sign + dt.strftime('%H:%M:%S')


def name_format(s):
    s1 = s.split('^')
    s2 = s1[0]
    s3 = f'{s2[:(s2 + " ").index(" ") + 2]}.[{s1[-1]}]'
    return s3


def check_cp(dist: list, data: DataFrame, name: str):  # ПЕРЕПИСАТЬ, ОСТАВЛЯЕТ ПУНКТЫ КОТОРЫХ НЕТ В ФРЕЙМЕ
    if '-' in dist:
        return dist
    else:
        # data.to_csv("data.csv")
        # print(name, name in list(data.index))
        s: Series = data.loc[name]
        # print(s.head(90))
        # Скрестили данные фрейма и дистанции, сделали перекрест
        not_null = [i for i in s.dropna(axis=0).index]
        # Выбрали только ненулевые, заново скрестили с дистанцией
        d = [i if i in not_null else '-' for i in dist]
        # except KeyError:
        #     d = []
        #     print('keyerror')
        return d


"""
1. Делаем фрейм с группой
2. Берем рассев этого человека
3. По очереди выводим его результаты, считаем проигрыш(+Проигрыш абсолютному лидеру, если не совпадают) и место
4. Считаем общюю статистику:
Проигрыш лидеру( \%)
Прооигрыш идеальному лидеру( \%)
Оценка
"""


def distance(routes: dict, name: str, group: str):
    d = routes[group]
    try:
        dist = eval([i for i in d if f'{name}^{group}' in d[i]][0])
    except:
        dist = [i for i in d if f'{name}^{group}' in d[i]][0]
    dist = [i if '0' not in str(i).split('->') else '-' for i in dist]
    return dist


def splits_list(name_data, dist, R):
    split_time = [name_data[dist[i]] if i != '-' else '-' for i in R]
    return split_time


def general_times_list(name_data, dist, nn, delim):
    part1 = dist[:nn[0]]
    part2 = dist[nn[-1] + 1:]
    try:
        general_time = [name_data[part1[:i]].sum() for i in range(1, len(part1) + 1)] + delim + [
            name_data['RES'] - name_data[part2[i:]].sum() for i in range(1, len(part2) + 1)]
    except:
        general_time = [''] * len(dist)
    return general_time


def find_num(dist, nn, R):
    num = [f'#{i + 1} [{dist[i]}]' if i != '-' else f'#{nn[0]}->#{nn[-1] + 1} Нет данных' for i in R]
    return num


def split_backlog(name_data, data, dist, R):
    define = [name_data[dist[i]] == data[dist[i]].sort_values().dropna().values[0] if i != '-' else '-' for i in R]
    backlog = [eval(f'{"1" if define[i] == False else "-1"}') * abs(
        name_data[dist[i]] - data[dist[i]].sort_values().dropna().values[0 if define[i] == False or len(
            data[dist[i]].sort_values().dropna().values) < 2 else 1]) if i != '-' else '-' for i in R]
    # [print(i,k) for i,k in zip(backlog, R)]
    print(name_data.dropna())
    percent_bk = [eval(f'{"1" if define[i] == False else "-1"}') * round(abs((name_data[dist[i]] * 100 / data[
        dist[i]].sort_values().dropna().values[0 if define[i] == False or len(
        data[dist[i]].sort_values().dropna().values) < 2 else 1]) - 100)) if i != '-' else '-' for i in R]
    return backlog, percent_bk


def find_nn(dist):
    if '-' in dist:
        nn = [n for n, i in enumerate(dist) if i == '-']
        delim = ['-'] * (nn[-1] - nn[0] + 1)
    else:
        nn = [len(dist)]
        delim = []
    return nn, delim


def split_leaders(data, dist, R):
    spl_leader = [f'{name_format(data.loc[:][dist[i]].sort_values().keys()[0])}' if i != '-' else '-' for i in R]
    return spl_leader


def split_place(name_data, data, dist, R):
    spl_place = [list(data[dist[i]].sort_values().values).index(name_data[dist[i]]) + 1 if i != '-' else '-' for i in R]
    return spl_place


def split_table_data(dist: list, data: DataFrame, name: str, group: str):
    name = f'{name.upper()}^{group.upper()}'
    dist = check_cp(dist, data, name)
    nn, delim = find_nn(dist)
    nn = sorted(nn)
    name_data = data.loc[name]
    # print(name_data.dropna(), nn)
    if list(name_data.dropna().index) == ['RES']:
        mode = 0
        col = ['n', 'gt', 's', 'bk', 'p_bk', 'l', 's_p']
        return pd.DataFrame(columns=col), mode
    else:
        mode = 1
    try:
        R = [r if r not in range(nn[0], nn[-1] + 1) else '-' for r in range(len(dist))]
        # ПОДПИСИ К ПУНКТАМ
        num = find_num(dist, nn, R)
        # СПЛИТЫ
        split_time = splits_list(name_data, dist, R)
        # ОБЩЕЕ ВРЕМЯ
        general_times = general_times_list(name_data, dist, nn, delim)
        # ОТСТАВАНИЕ
        backlog, percent_bk = split_backlog(name_data, data, dist, R)
        # ЛИДЕР НА ПЕРЕГОНАХ
        spl_leader = split_leaders(data, dist, R)
        # МЕСТО НА ПЕРЕГОНЕ
        split_places = split_place(name_data, data, dist, R)
        # СОЗДАТЬ ФРЕЙМ С ДАННЫМИ
        col = ['n', 'gt', 's', 'bk', 'p_bk', 'l', 's_p']
        val = [num, general_times, split_time, backlog, percent_bk, spl_leader, split_places]
        SPL = {k: v for k, v in zip(col, val)}
        df = pd.DataFrame(SPL).set_index(['n'])
        return df, mode
    except Exception as e:
        # print(e, 'error with split data', name)
        mode = 0
        col = ['n', 'gt', 's', 'bk', 'p_bk', 'l', 's_p']
        return pd.DataFrame(columns=col), mode


def SPL(split_input: SplitInput, results_data: Results):
    username = f'{split_input.user.first_name} {split_input.user.last_name}'
    splits = pd.DataFrame(results_data.splits['data'], index=results_data.splits['index'],
                          columns=results_data.splits['columns'])
    for column in splits.columns:
        splits[column] = splits[column].astype('timedelta64[ns]')
    name, group = find_most_similar_index(input_string=username, dataframe=splits)
    data = results_filter(splits, group=group, filt=split_input.sort_by)
    dist = distance(routes=results_data.routes, name=name.upper(), group=group.upper())
    # фрейм с основными данными сплита
    spl, mode = split_table_data(dist, data, name, group)
    spl.drop_duplicates(inplace=True)
    spl = spl.fillna('-')
    if mode == 1:
        # results_df, gen_res = results(splits, group, results_data.routes)
        # print(5)
        return spl
    else:
        # print("BAD SPLIT TABLE DATA /split.py")
        pass


def results(data, group, routes):
    names = [i for v in routes[group].values() for i in v]
    # Создание фрейма человек^группа : данные
    df = pd.DataFrame(index=names)
    df.index.name = 'name'
    # Заполнение результатов
    res_frame = data.loc[names]['RES']
    leader_res = res_frame.iloc[0]
    res = list(res_frame.values)
    # Заполнение отставаний
    backlogs = list(res_frame.apply(lambda x: x - leader_res if x != pd.NaT else pd.NaT))
    # Заполнение фрейма
    df['res'] = res
    df['l_bk'] = backlogs
    # Сбор рассевов этой группы
    group_routes = list(routes[group])
    # Люди с такими же дистанциями
    same_route_sportsmens = find_same_routes(group_routes, routes)
    # Результаты общей группы
    general_res_frame = pd.DataFrame(data.loc[same_route_sportsmens]['RES'].sort_values())
    leader_res2 = general_res_frame['RES'].values[0]
    general_res_frame['l_bk'] = list(
        general_res_frame['RES'].apply(lambda x: x - leader_res2 if x != pd.NaT else pd.NaT))
    return df, general_res_frame


def find_same_routes(group_routes, routes):
    groups = [gr for gr in routes for r in routes[gr] if r in group_routes]
    names = []
    for group in groups:
        names += [i for v in routes[group].values() for i in v]
    return list(set(names))


def find_most_similar_index(input_string: str, dataframe: pd.DataFrame) -> (str, str):
    indexes = {i.split("^")[0]: i for i in dataframe.index.tolist()}
    most_similar_index, similarity_score = process.extractOne(input_string, indexes.keys())
    if similarity_score < 90:
        return '0', '0'
    else:
        name = indexes[most_similar_index].split('^')[0]
        group = indexes[most_similar_index].split('^')[1]
        return name, group
