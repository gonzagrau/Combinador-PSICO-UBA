import pandas as pd
from combiner import *
from typing import Tuple
from datetime import time


# setup pandas display options
pd.set_option('display.width', 400)
pd.set_option("display.max_columns", 10)


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


def xlsx_to_subject(filepath: str) -> Subject:
    """
    This function parses the information given in an Excel file to
    Subject objects. The .xlsx is assumed to have either two or three
    sheets: TEO (theory classes), SEM (seminaries, optional), and COM
    (practical classes, which determine the actual comissions)
    """

    # Create subject object
    sub_name = filepath.split('/')[-1].strip('.xlsx')
    subject = Subject(sub_name)

    # Get dataframes
    try:
        teo_df = pd.read_excel(filepath, sheet_name='TEO')
        teo_df = teo_df.rename(str.strip, axis = 'columns')
        com_df = pd.read_excel(filepath, sheet_name='COM')
        com_df = com_df.rename(str.strip, axis = 'columns')
    except ValueError:
        raise ValueError('Invalid .xlsx file, either TEO or COM not found')

    try:
        sem_df = pd.read_excel(filepath, sheet_name='SEM')
        sem_df = sem_df.rename(columns=lambda x: x.strip())
    except ValueError:
        # if there are no seminaries for a given subject, sem_df is None
        sem_df = None

    def parse_df(df: pd.DataFrame) -> dict:
        """
        Same procedure used for teo_df and sem_df, function is defined inside this
        frame for ease of reading
        """

        cb_dict = {}
        for index, row in df.iterrows():
            weekday = row['Dia'].strip()
            start_time_str = row['Inicio']
            start_time = time(*str_to_time_tuple(start_time_str))
            end_time_str = row['Fin']
            end_time = time(*str_to_time_tuple(end_time_str))
            identifyer = row.iloc[0].strip()
            teacher = row['Profesor']
            observation = row['Observ.']
            if str(observation).strip() in ['nan', ' ', '.', '-']:
                # discard empty observations
                observation = ''
            new_cb = CourseBlock(weekday, start_time, end_time, teacher, observation)
            cb_dict[identifyer] = new_cb

        return cb_dict

    # parse theory df
    teo_cb_dict = parse_df(teo_df)

    # when possible, parse seminaries df
    if sem_df is not None:
        sem_cb_dict = parse_df(sem_df)

    print('-------TEORICOS--------\n')
    for key, val in teo_cb_dict.items():
        print(key)
        print(val)
        print()

    print('-------SEMINARIOS-------\n')
    for key, val in sem_cb_dict.items():
        print(key)
        print(val)
        print()

    return subject






if __name__ == '__main__':
    sub = xlsx_to_subject('subjects/Psicopato Naperstek.xlsx')