import os
import pandas as pd
import numpy as np
import requests

def load_data(url):
    """Load the raw data from the provided URL and save it to the 'data/raw/raw_data.csv' file."""
    response = requests.get(url)

    # Save the raw data to 'data/raw/raw_data.csv'
    file_path = os.path.join('data', 'raw', 'raw_data.csv')
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'wb') as f:
        f.write(response.content)

    # Read the CSV data
    data = pd.read_csv(file_path)

    return data

def clean_data(data):
    """Clean the raw data and save it to 'data/processed/cleaned_data.csv'."""
    # (1) Convert 'MonthlyIncome' and 'MonthlyRate' columns to float
    data[['MonthlyIncome', 'MonthlyRate']] = data[['MonthlyIncome', 'MonthlyRate']].astype(float)

    # (2) Convert specified columns to object data type
    columns_to_convert = ['Education', 'EnvironmentSatisfaction', 'JobInvolvement', 'JobLevel', 'JobSatisfaction',
                           'NumCompaniesWorked', 'PerformanceRating', 'RelationshipSatisfaction', 'StockOptionLevel',
                           'TrainingTimesLastYear', 'WorkLifeBalance']
    data[columns_to_convert] = data[columns_to_convert].astype(object)

    # (3) Set 'EmployeeNumber' as the index
    data.drop('EmployeeNumber', axis = 1, inplace=True)



    # (5) Save the cleaned data
    file_path = os.path.join('data', 'processed', 'clean_data.csv')
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    data.to_csv(file_path)

    return data

if __name__ == "__main__":
    url = "https://raw.githubusercontent.com/Romuald86github/Internship/main/employee_attrition.csv"
    raw_data = load_data(url)
    cleaned_data = clean_data(raw_data)