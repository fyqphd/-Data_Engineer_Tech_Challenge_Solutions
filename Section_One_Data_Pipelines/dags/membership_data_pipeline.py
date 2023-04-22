"""Copyright (C) XXX, 2023. All rights reserved.

Pipeline to ingest, clean, perform validity checks, and create membership IDs for successful applications.
"""
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import date, datetime, timedelta
import glob
import hashlib
import pandas as pd
import re
import time
import os

# set up input and output folders
input_folder = '/Users/yanqingfu/airflow/in'
successful_folder = '/Users/yanqingfu/airflow/successful'
unsuccessful_folder = '/Users/yanqingfu/airflow/unsuccessful'

# get today's date at 12:00 AM
today = datetime.now()
start_date = today.replace(hour=0, minute=0, second=0, microsecond=0)

# define DAG arguments
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=3),
    'start_date': start_date,
}

# define DAG
dag = DAG(
    'membership_data_pipeline',
    default_args=default_args,
    description='Pipeline to process membership applications',
    schedule=timedelta(hours=1),
    catchup=False,
)

# get first name and last name from full name
def extract_name_parts(name):
    regex = r'([A-Z][a-z]+) ([A-Z][a-z]+)'
    match = re.search(regex, name)
    if match:
        return match.group(1), match.group(2)

# format brithday as YYYYMMDD for different date formats
def format_dob(dob):
    formats = ['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y', '%Y/%m/%d']
    for date_format in formats:
        try:
            return datetime.strptime(dob, date_format).strftime('%Y%m%d')
        except ValueError:
            pass

# create memebership id based on last name and birthday hash
def generate_membership_id(row):
    hash_dob = hashlib.sha256(row['date_of_birth'].encode()).hexdigest()[:5]
    return f"{row['last_name']}_{hash_dob}"

# check for new csv files and load them into one dataframe
def get_new_csv_files():
    df = pd.DataFrame()
    # buffer time of 10 minutes
    minutes_ago = time.time() - 600
    all_files = glob.glob(input_folder + "/*.csv")
    # get all files that were added within the last 10 minutes
    new_files = [file for file in all_files if os.path.getmtime(file) >= minutes_ago]
    if new_files:
        df_list = [pd.read_csv(file) for file in new_files]
        df = pd.concat(df_list, ignore_index=True)
        return df

# clean and transform data
def format_data(df):
    if df is not None and not df.empty:
        # drop rows with missing values
        df.dropna(subset=['name', 'date_of_birth'], inplace=True)
        # remove duplicate rows based on all columns
        df.drop_duplicates(inplace=True)
        # get first name and last name
        df[['first_name', 'last_name']] = df['name'].apply(
            extract_name_parts).apply(pd.Series)
        # format date of birth
        df['date_of_birth'] = df['date_of_birth'].apply(format_dob)
        # remove spaces in mobile number
        df['mobile_no'] = df['mobile_no'].str.replace(' ', '')
        # check if age is above 18 years old as of 1 Jan 2022
        df['above_18'] = (pd.to_datetime('20220101',
                                        format='%Y%m%d') - pd.to_datetime(df['date_of_birth'],
                                                                        format='%Y%m%d')).dt.days > 18 * 365
        return df
    else:
        return pd.DataFrame()

# perform validity checks and create membership IDs for successful applications
def check_validity(df):
    result_dict = {}
    if df is not None and not df.empty:
        # check if mobile number is 8 digits, age is above 18 and email ends with .com or .net
        valid_mobile = df['mobile_no'].str.len() == 8
        valid_age = df['above_18']
        valid_email = df['email'].str.endswith(('.com', '.net'))
        # create membership id for successful applications
        successful_applications = df[valid_mobile & valid_age & valid_email].copy()
        successful_applications['membership_id'] = successful_applications.apply(
            generate_membership_id, axis=1)
        unsuccessful_applications = df[~(valid_mobile & valid_age & valid_email)]
        result_dict = {
            'successful_applications': successful_applications,
            'unsuccessful_applications': unsuccessful_applications
        }
        return result_dict
    else:
        return result_dict

# write results as csv files to different status folders
def output_csv_files(result_dict):
    if result_dict:
        successful_applications = result_dict['successful_applications']
        unsuccessful_applications = result_dict['unsuccessful_applications']
        # get the current datatime as YYYYMMDDHH
        now = datetime.now()
        formatted_datetime = now.strftime('%Y%m%d%H')
        # create folders if they don't exist
        for folder in [successful_folder, unsuccessful_folder]:
            if not os.path.exists(folder):
                os.makedirs(folder)
        # write csv files
        successful_applications.to_csv(
            successful_folder +
            '/successful_applications' +
            '_' +
            formatted_datetime +
            '.csv',
            index=False)
        unsuccessful_applications.to_csv(
            unsuccessful_folder +
            '/unsuccessful_applications' +
            '_' +
            formatted_datetime +
            '.csv',
            index=False)


# define task to get new csv files and load them into one dataframe
get_new_csv_files_task = PythonOperator(
    task_id='get_new_csv_files',
    python_callable=get_new_csv_files,
    dag=dag
)


# define task to format data and clean it
format_data_task = PythonOperator(
    task_id='format_data',
    python_callable=format_data,
    op_kwargs={'df': get_new_csv_files_task.output},
    dag=dag
)

# define task to check validity and create membership IDs
check_validity_task = PythonOperator(
    task_id='check_validity',
    python_callable=check_validity,
    op_kwargs={'df': format_data_task.output},
    dag=dag
)

# define task to write csv files to different status folders
output_csv_files_task = PythonOperator(
    task_id='output_csv_files',
    python_callable=output_csv_files,
    op_kwargs={'result_dict': check_validity_task.output},
    dag=dag
)
