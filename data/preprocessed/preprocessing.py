import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder, FunctionTransformer
from imblearn.over_sampling import RandomOverSampler
from scipy.stats import yeojohnson
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
import boto3

def remove_skewness(X):
    columns_to_transform = ['DistanceFromHome', 'TotalWorkingYears', 'YearsAtCompany']
    for col in columns_to_transform:
        X[col], _ = yeojohnson(X[col])
    return X


def load_data():
    data = pd.read_csv("data/processed/selected_data.csv")
    target_column = "Attrition"
    return data, target_column

def preprocess_data(data, target_column):
    X = data.drop(columns=[target_column])
    y = data[target_column]

    X = remove_skewness(X)


    # Encode target
    le = LabelEncoder()
    y = le.fit_transform(y)

    # Encode or get_dummies for categorical columns
    categorical_cols = X.select_dtypes(include='object').columns
    categorical_transformer = OneHotEncoder(handle_unknown='ignore')
    column_transformer = ColumnTransformer(
        transformers=[('categorical', categorical_transformer, categorical_cols)],
        remainder='passthrough'
    )

    # Balance target classes
    ros = RandomOverSampler(random_state=42)
    X, y = ros.fit_resample(X, y)

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.4, random_state=42)
    X_val, X_test, y_val, y_test = train_test_split(X_test, y_test, test_size=0.5, random_state=42)

    # Scale data
    scaler = StandardScaler()

    # Create preprocessing pipeline
    preprocessing_pipeline = Pipeline(steps=[
        ('column_transformer', column_transformer),
        ('scaler', scaler)
    ])

    X_train = preprocessing_pipeline.fit_transform(X_train)
    X_val = preprocessing_pipeline.transform(X_val)
    X_test = preprocessing_pipeline.transform(X_test)


    # Save the preprocessed data and pipeline to AWS S3
    save_to_s3(X_train, X_val, X_test, y_train, y_val, y_test, preprocessing_pipeline)

    return X_train, X_val, X_test, y_train, y_val, y_test

def save_to_s3(X_train, X_val, X_test, y_train, y_val, y_test, preprocessing_pipeline):
    # Ensure AWS credentials are set in the environment
    aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    aws_region = os.getenv('AWS_DEFAULT_REGION')

    # Set the S3 bucket and path
    bucket_name = "attritionproject"
    artifact_path = "attrition/artifacts"
    artifact_uri = f"s3://{bucket_name}/{artifact_path}"

    # Initialize boto3 client
    s3_client = boto3.client(
        's3',
        region_name=aws_region,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )

    # Save preprocessed data to S3
    pd.to_pickle((X_train, X_val, X_test, y_train, y_val, y_test), 'data/processed/preprocessed_data.pkl')
    s3_client.upload_file('data/processed/preprocessed_data.pkl', bucket_name, f"{artifact_path}/preprocessed_data.pkl")

    # Save preprocessing pipeline to S3
    import pickle
    with open('src/models/preprocessing_pipeline.pkl', 'wb') as f:
        pickle.dump(preprocessing_pipeline, f)
    s3_client.upload_file('src/models/preprocessing_pipeline.pkl', bucket_name, f"{artifact_path}/preprocessing_pipeline.pkl")
if __name__ == "__main__":
    data, target_column = load_data()
    X_train, X_val, X_test, y_train, y_val, y_test = preprocess_data(data, target_column)