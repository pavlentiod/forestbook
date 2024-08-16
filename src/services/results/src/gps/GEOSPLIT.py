# -*- coding: utf-8 -*-
import json
from io import BytesIO

import haversine
import pandas as pd
from fastapi import HTTPException, status
from fuzzywuzzy import process
from pandas import Timestamp, Timedelta

from EVENT_parser.Backend.SFR_parse import SFR_parsing
from EVENT_parser.Backend.SI_parse import SI_parsing
from EVENT_parser.Backend.common_functions import web_parse
from EVENT_parser.Backend.geotable import geotable
from EVENT_parser.Backend.split import SPL
from core.Storage import s3
from core.models import SD_Event_file




def find_most_similar_index(input_string: str, dataframe: pd.DataFrame) -> (str, str):
    indexes = {i.split("^")[0] : i for i in dataframe.index.tolist()}
    # index_choices =[i.split("^")[0] for i in dataframe.index.tolist()]
    most_similar_index, similarity_score = process.extractOne(input_string, indexes.keys())
    if similarity_score < 80:
        return '0', '0'
    else:
        name = indexes[most_similar_index].split('^')[0]
        group = indexes[most_similar_index].split('^')[1]
        return name, group


def stops_3sec_more(dft: pd.DataFrame) -> int:
    con = 0
    general = 0
    for pace in dft['spd']:
        if pace < 4:
            con += 1
        else:
            con = 0
        if con >= 3:
            general += 1
    return general


def calculate_metrics(dfs: pd.DataFrame, dft: pd.DataFrame) -> pd.DataFrame:
    start = dft.index.to_list()[0]
    dfs['n'] = dfs.index
    dfs.index = dfs['gt'].astype('timedelta64[ns]').apply(lambda x: start + x)
    control_points = get_control_points(dfs)
    dfa = {}
    coord = {}
    hav = lambda x, y: haversine.haversine(x, y) * 1e3
    for v, k in control_points.items():
        start_p = dft.loc[k[0], ['lat', 'lon']].values
        fin_p = dft.loc[k[1], ['lat', 'lon']].values
        d2d_straight = hav(start_p, fin_p)  # meters
        d2d_path = dft.loc[k[0]:k[1], 'dist_2d'].sum()
        alt_dif = dft.loc[k[1], 'alt'] - dft.loc[k[0], 'alt']
        climb = dft[dft['alt_diff'] > 0].loc[k[0]:k[1], 'alt_diff'].sum()
        down = dft[dft['alt_diff'] < 0].loc[k[0]:k[1], 'alt_diff'].sum()
        path_coef = d2d_path / d2d_straight if d2d_straight != 0 else 2
        spd_eff = (d2d_straight / (Timestamp(k[1]) - Timestamp(k[0])).total_seconds()) * 3.6  # km/h
        spd_real = (d2d_path / (Timestamp(k[1]) - Timestamp(k[0])).total_seconds()) * 3.6  # km/h
        spd_std = dft.loc[k[0]:k[1], 'spd'].std()
        spd_max = dft.loc[k[0]:k[1], 'spd'].max()
        spd_min = dft.loc[k[0]:k[1], 'spd'].min()
        pace = dft.loc[k[0]:k[1], 'pace'].median()
        stops = stops_3sec_more(dft.loc[k[0]:k[1], :])

        d = {
            'xy': d2d_straight,
            'path': d2d_path,
            'dif': path_coef,
            'a_dif': alt_dif,
            'climb': climb,
            'down': down,
            'spde': spd_eff,
            'spdr': spd_real,
            'spd_std': spd_std,
            'spd_max': spd_max,
            'spd_min': spd_min,
            'stops': stops,
            'pace': pace
        }
        dfa.setdefault(v, d)
        stx = dft.loc[k[0], 'lat']
        sty = dft.loc[k[0], 'lon']
        fnx = dft.loc[k[1], 'lat']
        fny = dft.loc[k[1], 'lon']
        coord.setdefault(v, {'stx': stx, 'sty': sty, 'fnx': fnx, 'fny': fny})
    coord_df = pd.DataFrame(coord)
    dfs.set_index('n', inplace=True)
    dfa = pd.DataFrame(dfa).T
    df_full = pd.concat([dfs, dfa], join='outer', axis=1)

    return df_full, coord_df


def get_control_points(dfs: pd.DataFrame) -> dict:
    control_points = {}
    for i in dfs.index:
        control_points.setdefault(dfs.loc[i, 'n'], (str(i - dfs.loc[i, 's']), str(i - Timedelta(seconds=1))))
    return control_points


async def GEOSPL(name, Files: SD_Event_file, filt='', gpxpath='', start='') -> (
        pd.DataFrame, pd.DataFrame, str, int, pd.Timedelta):
    # Get event data from DB
    f = await s3.download_object(key=Files.splits_path)
    df = pd.read_csv(BytesIO(f), index_col=0)
    for column in df.columns:
        df[column] = df[column].astype('timedelta64[ns]')

    r = await s3.download_object(key=Files.routes_path)
    routes = json.loads(r.decode('utf-8'))

    athlet_name, group = find_most_similar_index(name, df)

    if athlet_name == '0':
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Could not find this athlete')

    # Get splits data
    try:
        dfs, res_df = SPL(df=df, routes=routes, name=athlet_name, group=group, filt=filt)
        full_index = f'{athlet_name}^{group}'
        res = df.loc[full_index, 'RES']
        mode = False if gpxpath == '' else True
        if not mode:
            return dfs, res_df, full_index, mode, res, pd.DataFrame()
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail='Can\'t create post, check input data')

    # Add GPS data to split
    try:
        dft = await geotable(gpxpath, result=res, start_time=start)
        df, coord_df = calculate_metrics(dfs, dft)
        return df, res_df, full_index, mode, res, coord_df

    except Exception as e:
        print(e)
        mode = False
        return dfs, res_df, full_index, mode, res, pd.DataFrame()


def calculate_post_metrics(df: pd.DataFrame, res_df: pd.DataFrame, index: str, success_gpx: bool, gpxfile: str,
                           res: pd.Timedelta, coord_df: pd.DataFrame = pd.DataFrame()) -> dict:
    df: pd.DataFrame = df
    backlog: pd.Timedelta = res_df.loc[index, 'l_bk']
    vc = df['s_p'].value_counts()
    split_firsts = 0 if 1 not in vc else vc[1]
    place = res_df.sort_values(by='res', ascending=True).index.tolist().index(index) + 1
    p_bk_median = df[df['p_bk'] != '-']['p_bk'].median()
    points_number = df.shape[0]
    for c in ['gt', 's', 'bk']:
        df[c] = df[c].apply(lambda x: x.total_seconds() if x != '-' else '-')
    d = {
        'backlog': backlog.total_seconds(),
        'split_firsts': int(split_firsts),
        'place': place,
        'median_p_bk': float(p_bk_median),
        'result': res.total_seconds(),
        'points_number': points_number,
        'split': df.to_json(orient='split'),
        'index': index.title(),
        'gps': False,
        'lenght_s': 0,
        'lenght_p': 0,
        'climb': 0,
        'pace': 0,
        'location': '',
        'gpx_path': '',
        'coord_data': {}
    }

    if success_gpx:
        lenght_s = df['xy'].sum()
        lenght_p = df['path'].sum()
        climb = df[df['climb'] > 0]['climb'].sum()
        pace = df['pace'].median()
        d1 = {
            'location': '',
            'gpx_path': gpxfile,
            'lenght_s': round(lenght_s),
            'lenght_p': round(lenght_p),
            'climb': round(climb),
            'pace': round(pace, 2),
            'split': df.to_json(orient='split'),
            'gps': True,
            'coord_data': coord_df.to_json(orient='split')
        }
        for k in d1:
            d[k] = d1[k]
    return d


async def create_post(name: str, surname: str, Files: SD_Event_file, gpxfile: str = "", start: str = "",
                      filt="") -> dict:
    fullname = f'{name.upper()} {surname.upper()}'
    # General split and event data
    df, res_df, index, success_gpx, res, coord_df = await GEOSPL(Files=Files, name=fullname, gpxpath=gpxfile,
                                                                 start=start,
                                                                 filt=filt)
    # VALIDATE DATA
    post = calculate_post_metrics(df=df, res_df=res_df, index=index, success_gpx=success_gpx, gpxfile=gpxfile, res=res,
                                  coord_df=coord_df)
    return post
