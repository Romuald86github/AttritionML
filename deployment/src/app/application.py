import os
import pickle
import pandas as pd
import boto3
from flask import Flask, request, jsonify, render_template

# Flask application initialization
application = Flask(__name__, static_folder='/application/static', template_folder='/application/templates')

# Set up AWS credentials
aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
aws_region = 'eu-north-1'

# Set the S3 bucket and path
bucket_name = "attritionproject"
artifact_path = "attrition/artifacts"

# Initialize boto3 client
s3_client = boto3.client(
    's3',
    region_name=aws_region,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)

# Load the best model from S3
model_path = f"{artifact_path}/best_model.pkl"
local_model_path = os.path.join(".", "best_model.pkl")
s3_client.download_file(bucket_name, model_path, local_model_path)

with open(local_model_path, 'rb') as f:
    model = pickle.load(f)

# Load the preprocessing pipeline from S3
pipeline_path = f"{artifact_path}/preprocessing_pipeline.pkl"
local_pipeline_path = os.path.join(".", "preprocessing_pipeline.pkl")
s3_client.download_file(bucket_name, pipeline_path, local_pipeline_path)

with open(local_pipeline_path, 'rb') as f:
    preprocessing_pipeline = pickle.load(f)

@application.route('/')
def index():
    return render_template('index.html')

@application.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    df = pd.DataFrame([data])
    X_preprocessed = preprocessing_pipeline.transform(df)
    prediction = model.predict(X_preprocessed)
    return jsonify({'prediction': int(prediction[0])})

if __name__ == '__main__':
    # No need to specify the port here. Let the environment handle it.
    application.run(host='0.0.0.0')
