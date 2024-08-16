import requests
import pandas as pd
from services.parser.src.SFR_parse import SFR_parsing
from services.parser.src.SPORT_ORG_parse import SO_parsing
from services.parser.src.WinOrient_parse import SI_parsing
from services.parser.src.utils import bs


def calculate_results(splits_df):
    splits_df['group'] = [i.split('^')[-1] for i in splits_df.index]
    df = splits_df.loc[:, ('group', 'RES')]
    df['RES'] = df['RES'].apply(lambda x: x.total_seconds() if x != pd.NaT else 'DSQ')
    results = {}
    for i in df.groupby('group')['RES']:
        vals = i[1].sort_values(ascending=True)
        results.setdefault(i[0], dict(zip(vals.index, vals.tolist())))
    return results

def parse_event(page):
    title = str(page.find('title'))
    if 'WinOrient' in title:
        return SI_parsing(page)
    elif 'SportOrg' in title:
        return SO_parsing(page)
    else:
        return SFR_parsing(page)

def web_parse(link: str):
    content = ''
    if 'http' in link:
        response = requests.get(link)
        try:
            content = response.content.decode(response.apparent_encoding)
        except UnicodeEncodeError as e:
            content = ''
    soup_page = bs(content)
    return soup_page


def file_parse(data: bytes):
    pass