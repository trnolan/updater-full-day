#!/usr/bin/python

from flask import Flask
import sqlite3
import boto3
import simplejson
import csv
import datetime
import os.path
import requests
import json


app = Flask(__name__)
app.config.update(
    PROPAGATE_EXCEPTIONS = True
)

# All hardcoded variables would get moved into a YAML/properties file with more
# time
sqlite_conn = sqlite3.connect('/Users/Tyler/Documents/Updater_Full_Day/updater_data_extractor_2.db')
sqlite_cursor = sqlite_conn.cursor()
base_dir = '/Users/Tyler/Documents/Updater_Full_Day/tyler-nolan-full-day/mock_ftp_dir'
s3 = boto3.client('s3')
default_bucket = 'updater-integrations'
default_api_endpoint='https://private-b4657-samplemoverapijson.apiary-mock.com/movers'

def update_db(client_id, source_type, row_data):
    try:
	sqlite_cursor.execute("INSERT INTO extracted_data VALUES (?, ?, ?, ?)", (client_id, datetime.datetime.utcnow(), source_type, str(row_data)))
	sqlite_conn.commit()
    except Exception as e:
	sqlite_conn.close()
	print e

def load_csv_return_rows(file_path):
    with open(file_path, 'rb') as csvfile:
	reader = csv.DictReader(csvfile)
	for row in reader:
		yield row

def load_json_return_rows(file_path):
    json_obj = simplejson.load(file_path)
    for row in json_obj:
	yield row

@app.route('/ftp_post/<client_id>/<file_name>', methods=['POST'])
def ftp_file_load(client_id, file_name):
    file_type = file_name.split('.')[1]
    file_path = os.path.join(base_dir, str(client_id), str(file_name))
    if file_type == 'csv':
	for line in load_csv_return_rows(file_path):
		update_db(client_id, 'ftp', line)
    elif file_type == 'json':
	for line in load_json_return_rows(file_path):
		update_db(client_id, 'ftp', line)
    return '200 OK'

@app.route('/s3_post/<client_id>/<key>', methods=['POST'])
def s3_file_load(client_id, key):
    for line in s3.get_object(Bucket=default_bucket,Key=key)['Body'].read().splitlines():
	update_db(client_id, 's3', line)
    return '200 OK'


@app.route('/remote_api_post/<client_id>', methods=['POST'])
def remote_api_load(client_id):
    r = requests.get(default_api_endpoint)
    for line in json.loads(r.text)['movers']:
	update_db(client_id, 'remote_api', line)
    return '200 OK'

if __name__ == '__main__':
    app.run()
