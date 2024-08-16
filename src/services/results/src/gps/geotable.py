# -*- coding: utf-8 -*-
from io import BytesIO, StringIO

import haversine
import numpy as np
import pandas as pd
from gpxcsv import gpxtolist
from pandas import Timestamp, Timedelta
from timezonefinder import TimezoneFinder

from core.Storage import s3


async def create_dataframe(path):
    ## GPXCSV
    f = await s3.download_object(key=path)
    s = StringIO(BytesIO(f).getvalue().decode('utf-8'))
    gpx_list = gpxtolist(s)
    df2 = pd.DataFrame(gpx_list)

    c = []
    for i in df2.columns:
        if i == 'lat':
            c.append('latitude')
        elif i == 'lon':
            c.append('longitude')
        elif i == 'ele':
            c.append('altitude')
        else:
            c.append(i)
    # print(c)
    df2.columns = c
    df = df2.loc[:, ('time', 'latitude', 'longitude', 'altitude')]

    tf = TimezoneFinder()
    v = df.values[0]
    tz = tf.timezone_at(lng=v[2], lat=v[1])
    df['time'] = df['time'].astype(f'datetime64[ns, {tz}]')

    ## GPX Converter
    # df = Converter(input_file=path).gpx_to_dataframe()

    try:
        df['time'] = df['time'].apply(lambda x: x.tz_convert(tz))
    except:
        df['time'] = df['time'].apply(lambda x: x.tz_localize('GMT'))
        df['time'] = df['time'].apply(lambda x: x.tz_convert(tz))
    df.set_index('time', inplace=True)
    if 'altitude' not in df.columns:
        df['altitude'] = [0] * df.shape[0]
    # print(tz, df)
    # df.to_csv('alex.csv')
    return df, tz


def find_start_index(df, tz, start_time=''):
    ind = list(df.index)
    date = ind[0]
    if start_time != '':
        start_timestamp = Timestamp(f'{date} {start_time}', tz=tz)
        start = df[df.index == start_timestamp].index[0]
    else:
        start_timestamp = [i for i in list(df.index)[:59] if i.second % 60 == 0][0]
        start = df[df.index == start_timestamp].index[0]
    return start


def interpolate_data(df, result, tz):
    result = int(Timedelta(result).total_seconds())
    ind = list(df.index)
    date = ind[0]
    result = result + 10000
    df2 = pd.DataFrame()
    df2.index = pd.Index([Timestamp(date) + Timedelta(seconds=i) for i in range(result)], dtype=f'datetime64[ns, {tz}]')
    df2['lat'], df2['lon'], df2['alt'] = [np.NaN] * result, [np.NaN] * result, [np.NaN] * result
    df2.loc[ind] = df.values
    df2.interpolate(inplace=True)
    df2 = df2.iloc[:result - 10000, :]
    a = 0
    for i in df2['alt']:
        if i > 0:
            a = i
            break
    df2['alt'] = df2['alt'].fillna(a)
    return df2


def hav_dist(x, y):
    return haversine.haversine(x, y) * 1e3


def calculate_distances(df):
    alt_del = [df.iloc[i, 2] - df.iloc[i - 1, 2] for i in range(1, len(df))]
    points = [(df.iloc[i, 0], df.iloc[i, 1]) for i in range(len(df))]
    dist_2d = [0] + [hav_dist(points[i - 1], points[i]) for i in range(1, len(df))]  # m
    dist_3d = [0] + [np.sqrt(dist_2d[i - 1] ** 2 + alt_del[i - 1] ** 2) for i in range(1, len(df))]  # m
    df['dist_2d'] = dist_2d
    df['dist_3d'] = dist_3d
    df['alt_diff'] = [0] + alt_del
    return df


def calculate_speed_pace(df):
    df['time_d'] = [1] * df.shape[0]
    df['spd'] = (df['dist_3d'] / df['time_d']) * 3.6  # km/h
    df['spd'] = df['spd'].apply(lambda x: 1 if x < 1 else x)  # km/h
    df['pace'] = 60 / df['spd']  # min/km
    return df


def fill_to_start(df, start, tz):
    ind = df.index.tolist()
    # print(start, pd.Timedelta(str(ind[0].time())))
    d = int((pd.Timedelta(start) - pd.Timedelta(str(ind[0].time()))).total_seconds())
    losted = 1 if d < 0 else 0
    start = Timestamp(f'{ind[0].date()} {start}', tz=tz)
    if losted == 1:
        t_index = [start + Timedelta(seconds=i) for i in range(abs(d))] + ind
        df_comp = pd.DataFrame(index=pd.Index(t_index, dtype=f'datetime64[ns, {tz}]'), columns=['lat', 'lon', 'alt'])
        df_comp.loc[:, :] = [df.iloc[0, :]] * len(t_index)
        df_comp.loc[:, :] = [df.iloc[0, :]] * len(t_index)
        df_comp.loc[ind, :] = df.values
        df = df_comp
        return df
    elif start not in ind:
        move_ind = [i for i in ind if i > start][0]
        df1 = df.loc[move_ind:, :]
        df2 = df1.iloc[:1, :]
        df2.index = [str(start)]
        df = pd.concat([df2, df1], join='outer', axis=0)
        df.index = df.index.astype(f'datetime64[ns, {tz}]')
        return df
    else:
        return df


async def geotable(path, start_time='', result=''):
    df, tz = await create_dataframe(path)
    if start_time == '':
        start_time = str(df.index.tolist()[0].time())
    df = fill_to_start(df, start_time, tz)
    st = find_start_index(df, start_time=start_time, tz=tz)
    df = df.loc[st:, :]
    df = interpolate_data(df, result, tz)
    df = calculate_distances(df)
    df = calculate_speed_pace(df)
    return df
