# names = [name1^group.upper(),...]
# points_l = {name1^group.upper() : [point1-> point2,...], ...}
# splits_l = {name1^group.upper() : [Timedelta('0 days 00:00:00'),...], ...}
# results = { name1^group.upper() : Timedelta('0 days 00:00:00'),...}
import json

import pandas as pd
from pandas import Timedelta

from services.parser.src.utils import course, dispersions


def SO_parsing(soup):
    data = str(soup).splitlines()
    race_line = [i for i in data if "var race =" in i][0]
    race_data = race_line[race_line.index("{"):-1]
    race = json.loads(race_data)

    groups = {p["id"]: p for p in race['groups']}
    persons = {p["id"]: p for p in race['persons']}
    results = {p["person_id"]: p for p in race['results']}
    # courses = {p["id"]: p for p in race['courses']}

    points_l, routes = {}, {}
    gen_df = pd.DataFrame()

    for group_id in groups:
        group_persons = [i for i in persons if persons[i]['group_id'] == group_id]
        for person_id in group_persons:
            person = persons[person_id]
            try:
                nickname = (
                    f"{person['surname']} {person['name']}^{groups[person['group_id']]['name'].split(' ')[0]}").upper()
                checked_points = [i for i in results[person_id]['splits'] if i['leg_time'] > 0]
                points = [{'code': '241'}] + checked_points + [{'code': '240'}]
                legs = course([int(points[i]["code"]) for i in range(len(points))])
                result = Timedelta(milliseconds=int(results[person['id']]['result_msec']))
                splits = [Timedelta(milliseconds=i['leg_time']) for i in points[1:-1]]
                splits += [result - Timedelta(milliseconds=points[-2]['relative_time'])]
                relative_times = [i['relative_time'] for i in checked_points]
                check_gen_times = [i + 1 for i in range(len(relative_times) - 1) if
                                   relative_times[i] > relative_times[i + 1]]
                df = pd.DataFrame(index=legs, columns=[nickname], data=splits, dtype="timedelta64[ns]").T
                if len(check_gen_times) > 0:
                    df.iloc[:, check_gen_times + [check_gen_times[-1] + 1]] = pd.NaT
                points_l.setdefault(nickname, legs)
                df["RES"] = result
                print(nickname, len(legs)  == len(splits))
                gen_df = pd.concat([gen_df, df], join='outer', axis=0)
            except Exception as e:
                print(e)
                continue
        routes.setdefault(groups[group_id]['name'].upper().split(' ')[0], dispersions(points_l.copy()))
        points_l.clear()
    gen_df.to_csv('gen3.csv')
    return gen_df, routes
