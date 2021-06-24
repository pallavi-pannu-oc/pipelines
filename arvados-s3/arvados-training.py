import json
import os

import boto3
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier

DATA_DIR = "/opt/dkube/input"
config = json.load(open(os.path.join(DATA_DIR, "config.json")))
with open(os.path.join(DATA_DIR, "credentials"), "r") as f:
    creds = f.read()
access_key = creds.split("\n")[1].split("=")[-1].strip()
secret_key = creds.split("\n")[2].split("=")[-1].strip()

session = boto3.session.Session()
s3_client = boto3.resource(
    service_name="s3",
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    endpoint_url=config["Endpoint"],
)

my_bucket = s3_client.Bucket(config["Bucket"])
s3_client.Bucket(config["Bucket"]).download_file("CMU-1/Data0000.dat", "Data0000.dat")
MODEL_DIR = "/opt/dkube/output/"

arv_data = np.fromfile("Data0000.dat", dtype=float)
arv_data = arv_data[~np.isnan(arv_data)]
arv_data = arv_data.reshape(-1, 1)
arv_data[arv_data <= 1e308] = 0
y_values = [0 if i % 2 == 0 else 1 for i in range(1, 91)]

### Training the model ###
arv_clf = RandomForestClassifier(max_depth=2, random_state=0)
arv_clf.fit(arv_data, y_values)

filename = os.path.join(MODEL_DIR, "model.joblib")
joblib.dump(arv_clf, filename)
