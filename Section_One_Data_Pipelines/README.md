## Pipeline for Membership Applications Processing

This document describes the design and implementation of a pipeline to process membership applications for an e-commerce company. 
The pipeline will ingest, clean, perform validity checks, and create membership IDs for successful applications.

### Prerequisites
- Python 3.10
- Apache Airflow 2.5.3
- SQLAlchemy 1.4.41

### Data Assumptions
- No middle name present in the name column
- No area code in the mobile_no column

### Pipeline Components

Assume that the pipeline finishes within 30 minutes when it starts.
For example, if the pipeline starts at 8:00 am, it should finish at 8:30 am.

The pipeline consist of four components

1. Data Ingestion

  task id get_new_csv_files
  
  check if any new file in the targeted folder with a buffer time 10 minutes
if there are new files, combine them into one dataframe

2. Data Cleaning and Transformation

  task id format_data
  
* remove rows with missing values on name and date_of_birth column
* remove duplicate rows
* separate name column into first name and last name using regular expression, which ignores suffix and prefix
* format date_of_birth column as YYYYMMDD
* remove spaces in mobile_no column
* add above_18 column as of 1 Jan 2022

3. Perform Validity Checks

  task id check_validity
  
successful applications critira: 
* mobile_no column has a length of 8
* age above 18
* email ends with .com or .net

Create membership id for successful applications.

4. Write Results to Folders

  task id output_csv_files
  
  for sucessful applications, the data is store at the successful folder, otherwise, in unsuccessful_folder


### Pipeline Test Run Results

![result image](./images/run_result.png)


### Suggestions to Upstream

Enforce the following rules, which will make the whole application process more efficient and effective.

* No suffix or prefix allowed, just have first name and last name input boxes
* Only allow one format for birthdate
* Check the length of the phone number; otherwise, don't allow submission
