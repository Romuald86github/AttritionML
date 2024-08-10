import pandas as pd



def load_data():
    data = pd.read_csv("data/processed/clean_data.csv")
    return data


def select_features(data, selected_features):
    selected_data = data[selected_features]
    selected_data.to_csv("data/processed/selected_data.csv", index=False)
    return selected_data

if __name__ == "__main__":
    data = load_data()
    selected_features = ['DailyRate', 'DistanceFromHome', 'EnvironmentSatisfaction',
                         'JobInvolvement', 'JobSatisfaction', 'MaritalStatus', 'NumCompaniesWorked',
                         'OverTime', 'StockOptionLevel', 'TotalWorkingYears', 'TrainingTimesLastYear',
                         'WorkLifeBalance', 'YearsAtCompany', 'Attrition']
    select_features(data, selected_features)
    
