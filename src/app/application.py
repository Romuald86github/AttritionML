import os
import mlflow
import mlflow.sklearn
from flask import Flask, request, jsonify, render_template, send_from_directory
import pandas as pd
import boto3
import pickle
from evidently.dashboard import Dashboard
from evidently.tabs import DataDriftTab, NumericStabilityTab, CatTargetDriftTab

app = Flask(__name__, static_folder='/app/static', template_folder='/app/templates')

# Set up AWS credentials
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

# Load the best model from S3
model_name = "RandomForestClassifier"
model_version = "1"
model_path = f"s3://{bucket_name}/{artifact_path}/best_model.pkl"

local_model_path = os.path.join(".", "best_model.pkl")
s3_client.download_file(bucket_name, f"{artifact_path}/best_model.pkl", local_model_path)

with open(local_model_path, 'rb') as f:
    model = pickle.load(f)

# Load the preprocessing pipeline from S3
preprocessing_pipeline_path = f"s3://{bucket_name}/{artifact_path}/preprocessing_pipeline.pkl"
local_pipeline_path = os.path.join(".", "preprocessing_pipeline.pkl")
s3_client.download_file(bucket_name, f"{artifact_path}/preprocessing_pipeline.pkl", local_pipeline_path)

with open(local_pipeline_path, 'rb') as f:
    preprocessing_pipeline = pickle.load(f)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    df = pd.DataFrame([data])
    X_preprocessed = preprocessing_pipeline.transform(df)
    prediction = model.predict(X_preprocessed)

    # Log the prediction to Evidently
    evidently_dashboard = Dashboard(tabs=[DataDriftTab(), NumericStabilityTab(), CatTargetDriftTab()])
    evidently_dashboard.calculate(df, X_preprocessed, prediction)
    evidently_dashboard.save_html(os.path.join('/app/static', 'evidently_report.html'))

    return jsonify({'prediction': int(prediction[0])})

@app.route('/evidently_report')
def serve_evidently_report():
    return send_from_directory('/app/static', 'evidently_report.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5010)