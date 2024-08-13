import os
import pickle
import mlflow
import mlflow.sklearn
import json
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import boto3
import numpy as np

def load_data():
    with open('data/processed/preprocessed_data.pkl', 'rb') as f:
        X_train, X_val, X_test, y_train, y_val, y_test = pickle.load(f)
    return X_train, X_val, X_test, y_train, y_val, y_test

def train_and_evaluate_models(X_train, y_train, X_val, y_val, X_test, y_test):
    # Set MLflow server and tracking URI
    mlflow.set_tracking_uri("http://localhost:5001")

    # Set the experiment name
    mlflow.set_experiment("predict-attrition")

    mlflow.set_artifact_uri("s3://attritionproject/attrition/artifacts")

    # Set S3 bucket and path for artifact storage
    aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    aws_region = os.getenv('AWS_DEFAULT_REGION')
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

    models = [
        RandomForestClassifier(random_state=42)
    ]

    best_model = None
    best_score = 0

    for model in models:
        with mlflow.start_run():
            model.fit(X_train, y_train)
            y_pred_val = model.predict(X_val)
            y_pred_test = model.predict(X_test)

            val_accuracy = accuracy_score(y_val, y_pred_val)
            test_accuracy = accuracy_score(y_test, y_pred_test)
            val_precision = precision_score(y_val, y_pred_val, pos_label=1)
            test_precision = precision_score(y_test, y_pred_test, pos_label=1)
            val_recall = recall_score(y_val, y_pred_val, pos_label=1)
            test_recall = recall_score(y_test, y_pred_test, pos_label=1)
            val_f1 = f1_score(y_val, y_pred_val, pos_label=1)
            test_f1 = f1_score(y_test, y_pred_test, pos_label=1)
            val_roc_auc = roc_auc_score(y_val, model.predict_proba(X_val)[:, 1])
            test_roc_auc = roc_auc_score(y_test, model.predict_proba(X_test)[:, 1])

            if val_roc_auc > best_score:
                best_model = model
                best_score = val_roc_auc

            mlflow.log_param("model", type(model).__name__)
            mlflow.log_metric("val_accuracy", val_accuracy)
            mlflow.log_metric("test_accuracy", test_accuracy)
            mlflow.log_metric("val_precision", val_precision)
            mlflow.log_metric("test_precision", test_precision)
            mlflow.log_metric("val_recall", val_recall)
            mlflow.log_metric("test_recall", test_recall)
            mlflow.log_metric("val_f1", val_f1)
            mlflow.log_metric("test_f1", test_f1)
            mlflow.log_metric("val_roc_auc", val_roc_auc)
            mlflow.log_metric("test_roc_auc", test_roc_auc)
            mlflow.sklearn.log_model(model, artifact_path="RandomForestClassifier")

    # Perform hyperparameter tuning on the best model
    if isinstance(best_model, RandomForestClassifier):
        param_grid = {
            'n_estimators': [100, 200, 300],
            'max_depth': [5, 10, 15],
            'min_samples_split': [2, 5, 10]
        }

        grid_search = GridSearchCV(best_model, param_grid, cv=5, scoring='roc_auc')
        grid_search.fit(X_train, y_train)

        best_model = grid_search.best_estimator_
        y_pred_val = best_model.predict(X_val)
        y_pred_test = best_model.predict(X_test)

        val_accuracy = accuracy_score(y_val, y_pred_val)
        test_accuracy = accuracy_score(y_test, y_pred_test)
        val_precision = precision_score(y_val, y_pred_val, pos_label=1)
        test_precision = precision_score(y_test, y_pred_test, pos_label=1)
        val_recall = recall_score(y_val, y_pred_val, pos_label=1)
        test_recall = recall_score(y_test, y_pred_test, pos_label=1)
        val_f1 = f1_score(y_val, y_pred_val, pos_label=1)
        test_f1 = f1_score(y_test, y_pred_test, pos_label=1)
        val_roc_auc = roc_auc_score(y_val, best_model.predict_proba(X_val)[:, 1])
        test_roc_auc = roc_auc_score(y_test, best_model.predict_proba(X_test)[:, 1])

        # Log the metadata
        metadata = {
            "dataset": "HR Analytics",
            "version": "1.0",
            "description": "This is the HR Analytics dataset used for the training experiment.",
            "features": ["DailyRate", "DistanceFromHome", "EnvironmentSatisfaction", "JobInvolvement", "JobSatisfaction", "MaritalStatus", "NumCompaniesWorked", "OverTime", "StockOptionLevel", "TotalWorkingYears", "TrainingTimesLastYear", "WorkLifeBalance", "YearsAtCompany"],
            "target": "Attrition"
        }
        with open("metadata.json", "w") as f:
            json.dump(metadata, f)
        mlflow.log_artifact("metadata.json", "metadata")

        mlflow.log_params(grid_search.best_params_)
        mlflow.log_metric("val_accuracy", val_accuracy)
        mlflow.log_metric("test_accuracy", test_accuracy)
        mlflow.log_metric("val_precision", val_precision)
        mlflow.log_metric("test_precision", test_precision)
        mlflow.log_metric("val_recall", val_recall)
        mlflow.log_metric("test_recall", test_recall)
        mlflow.log_metric("val_f1", val_f1)
        mlflow.log_metric("test_f1", test_f1)
        mlflow.log_metric("val_roc_auc", val_roc_auc)
        mlflow.log_metric("test_roc_auc", test_roc_auc)
        mlflow.sklearn.log_model(best_model, artifact_path="RandomForestClassifier", registered_model_name="RandomForestClassifier")

        # Save the model to S3
        model_dir = os.path.join(artifact_path)
        os.makedirs(model_dir, exist_ok=True)
        model_path = os.path.join(model_dir, 'best_model.pkl')
        with open(model_path, 'wb') as f:
            pickle.dump(best_model, f)
        s3_client.upload_file(model_path, bucket_name, f"{artifact_path}/best_model.pkl")
        os.remove(model_path)

        print(f"Tuned RandomForestClassifier validation accuracy: {val_accuracy}, test accuracy: {test_accuracy}")

    return best_model

if __name__ == "__main__":
    X_train, X_val, X_test, y_train, y_val, y_test = load_data()
    train_and_evaluate_models(X_train, y_train, X_val, y_val, X_test, y_test)
