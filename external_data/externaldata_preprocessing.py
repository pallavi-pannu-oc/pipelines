import boto3
import json
import os
import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier

DATA_DIR = '/opt/dkube/input'

config = json.load(open(os.path.join(DATA_DIR,'config.json')))

with open(os.path.join(DATA_DIR,'credentials'), 'r') as f:
    creds = f.read()
       
access_key = creds.split('\n')[1].split('=')[-1].strip()
secret_key = creds.split('\n')[2].split('=')[-1].strip()

session = boto3.session.Session()
s3_client = boto3.resource(
    service_name='s3',
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    endpoint_url=config['Endpoint']
)

s3_client.Bucket(config['Bucket']).download_file('datasets/heart-data/heart.csv', 'heart.csv')

## Preprocessed training data
train_data=pd.read_csv('heart.csv')
train_data = train_data.drop('ca',axis = 1)






