import pandas as pd
from typing import Tuple
import os
from datetime import time
import combiner
import re
from typing import List

# setup pandas display options
pd.set_option('display.width', 400)
pd.set_option("display.max_columns", 10)

ROMAN_CONSTANTS = ("I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "XI", "XII", "XII", "XIV", "XV" )

def is_roman_number(num: str):
    """
    checks whether a str is a (small) roman numeral
    """
    pattern = re.compile(r"^(X{0,3})(IX|IV|V?I{0,3})$", re.VERBOSE)
    return bool(re.match(pattern, num))


def str_to_time_tuple(time_str: str) -> Tuple[int, int]:
    """
    :param time_str: string starting in 'hh' and ending in 'mm', where h and m are ints
    :return: int tuple (hh, mm)
    """
    time_str = time_str.strip()
    assert len(time_str) > 3, f'time_str too short, len == {len(time_str)}'
    try:
        hh = int(time_str[:2])
        mm = int(time_str[-2:])
    except ValueError:
        raise ValueError("Invalid hour or minute")
    assert hh // 24 == 0 and hh >= 0, f'Hour must be in range(24), got hour == {hh}'
    assert mm // 60 == 0 and mm >= 0, f'minute must be in range(60), got minute == {mm}'

    return hh, mm


def parse_course_blocks(df: pd.DataFrame) -> dict:
    """
    Get course blocks from a website-like dataframe
    """

    cb_dict = {}
    for index, row in df.iterrows():
        weekday = row['Dia'].strip()
        start_time_str = row['Inicio']
        start_time = time(*str_to_time_tuple(start_time_str))
        end_time_str = row['Fin']
        end_time = time(*str_to_time_tuple(end_time_str))
        identifyer = str(row.iloc[0]).strip().upper()
        teacher = row['Profesor']
        observation = row['Observ.']
        if str(observation).strip() in ['nan', ' ', '.', '-']:
            # discard empty observations
            observation = ''
        else:
            observation = '\n'.join(re.split(r'[.\-]', observation))
        new_cb = combiner.CourseBlock(weekday, start_time, end_time, teacher, observation)
        cb_dict[identifyer] = new_cb

    return cb_dict


def dfs_to_subject(name: str, teo_df: pd.DataFrame, com_df: pd.DataFrame, sem_df: pd.DataFrame = None) -> combiner.Subject:
    """
    This function parses the information from the format given in the website
    to the internal representation of this project using Subject objects
    """
    subject = combiner.Subject(name)

    # get course blocks from dataframes
    teo_cb_dict = parse_course_blocks(teo_df)
    if sem_df is not None:
        sem_cb_dict = parse_course_blocks(sem_df)
    else:
        sem_cb_dict = {}
    com_dict = parse_course_blocks(com_df)

    # build actual comissions
    for index, row in com_df.iterrows():
        identifyer = str(row['Comisiones']).strip()
        new_com = combiner.Comission(identifyer)

        # add course blocks
        keys = [x.strip() for x in row['Oblig.'].strip().split(' - ')]
        teo_keys = [key for key in keys if is_roman_number(key)]
        for teo_key in teo_keys:
            teo_cb = teo_cb_dict[teo_key]
            new_com.add_course_block(teo_cb)
            keys.remove(teo_key)
        if sem_df is not None:
            # the only keys left, if any, are seminary keys
            for sem_key in keys:
                sem_cb = sem_cb_dict[sem_key]
                new_com.add_course_block(sem_cb)

        com_cb = com_dict[identifyer]
        new_com.add_course_block(com_cb)

        # add comission to subject
        subject.append_comission(new_com)

    return subject


def url_parse(url: str) -> combiner.Subject:
    """
    Retrieves the information from a URL, and returns the parsed subject
    """
    # read all html tables on the webpage as dataframes
    dfs = pd.read_html(url)
    if not len(dfs):
        raise ValueError('Invalid URL: no tables found at all')

    # first df holds the subject name in the format ( <number> - <name> )
    title_df = dfs.pop(0)
    raw_name = title_df.iloc[0,0]
    match = re.search(r'\(\s\d+\s-(.*?)\)', raw_name)
    if match:
        name = match.group(1)
        if len(name) > 30:
            # adjust name lenght
            words = name.split(' ')
            start_words = words[:len(words)//2]
            end_words = words[len(words)//2:]
            name = ' '.join(start_words) + ' \n' + ' '.join(end_words)
    else:
        raise ValueError('Invalid URL: no subject name found')

    # find other dfs
    df_dict = {}
    for df in dfs:
        key = df.columns[0]
        df_dict[key] = df

    try:
        teo_df = df_dict['Teóricos']
        com_df = df_dict['Comisiones']
    except KeyError:
        raise ValueError('Invalid URL: obligatory tables not found')

    # seminaries are optional
    try:
        sem_df = df_dict['Seminarios']
    except KeyError:
        sem_df = None

    return dfs_to_subject(name, teo_df, com_df, sem_df)


def test():
    # url parse test
    base_url = "http://academica.psi.uba.ar/Psi/Ver154_.php?catedra="
    dfs = pd.read_html("http://academica.psi.uba.ar/Psi/Ope154_.php")
    catedras_df = dfs[2]
    for index, row in catedras_df.head(20).iterrows():
        subject = url_parse(f"{base_url}{row[0]}")
        print(subject)


if __name__ == '__main__':
    test()
