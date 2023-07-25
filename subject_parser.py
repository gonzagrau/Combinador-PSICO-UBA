import pandas as pd
from combiner import *
from typing import Tuple
from datetime import time
import os
from combiner import *


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
    sub_name = os.path.basename(filepath).strip('.xlsx')
    subject = Subject(sub_name)

    # Get dataframes
    try:
        teo_df = pd.read_excel(filepath, sheet_name='TEO')
        teo_df = teo_df.rename(str.strip, axis = 'columns')
        prac_df = pd.read_excel(filepath, sheet_name='COM')
        prac_df = prac_df.rename(str.strip, axis = 'columns')
    except ValueError:
        raise ValueError('Invalid .xlsx file, either TEO or COM not found')

    try:
        sem_df = pd.read_excel(filepath, sheet_name='SEM')
        sem_df = sem_df.rename(columns=lambda x: x.strip())
    except ValueError:
        # if there are no seminaries for a given subject, sem_df is None
        sem_df = None

    def parse_course_blocks(df: pd.DataFrame) -> dict:
        """
        Same procedure used for all dataframes, function is defined inside this
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

    # get course blocks from dataframes
    teo_cb_dict = parse_course_blocks(teo_df)
    if sem_df is not None:
        sem_cb_dict = parse_course_blocks(sem_df)
    else:
        sem_cb_dict = {}
    com_dict = parse_course_blocks(prac_df)

    # build actual comissions
    for index, row in prac_df.iterrows():
        identifyer = row['Comisiones'].strip()
        new_com = Comission(identifyer)

        # add course blocks
        if sem_df is not None:
            teo_key, sem_key = row['Oblig.'].strip().split(' - ')
            try:
                sem_cb = sem_cb_dict[sem_key]
                new_com.add_course_block(sem_cb)
            except KeyError:
                # sometimes, keys are swapped. this is easily fixed
                teo_key, sem_key = sem_key, teo_key
                sem_cb = sem_cb_dict[sem_key]
                new_com.add_course_block(sem_cb)
        else:
            teo_key = row['Oblig.'].strip()
        teo_cb = teo_cb_dict[teo_key]
        new_com.add_course_block(teo_cb)
        com_cb = com_dict[identifyer]
        new_com.add_course_block(com_cb)

        # add comission to subject
        subject.append_comission(new_com)

    return subject


def parse_all_subjects(directory: str) -> List[Subject]:
    """
    parses all subjects from a giver directory
    """
    subjects = []
    for filename in os.listdir(directory):
        _, file_extension = os.path.splitext(filename)
        f = os.path.join(directory, filename)
        # checking if it is a valid file
        if os.path.isfile(f) and file_extension == '.xlsx':
            sub = xlsx_to_subject(f)
            subjects.append(sub)
    return subjects


def test():
    subjects = parse_all_subjects('subjects')
    combinations = find_combinations(subjects)
    for sub in subjects:
        print(sub)
    return  subjects, combinations


if __name__ == '__main__':
    test()
