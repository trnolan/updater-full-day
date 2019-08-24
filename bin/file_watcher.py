#!/usr/bin/python

import sys
import os
import os.path
import requests


base_dir = '/Users/Tyler/Documents/Updater_Full_Day/tyler-nolan-full-day/mock_ftp_dir'
archive_dir = '/Users/Tyler/Documents/Updater_Full_Day/tyler-nolan-full-day/mock_ftp_archive_dir'

def archive_file(sub_dir, data_file):
    if not os.path.isdir(os.path.join(archive_dir, sub_dir)):
	os.mkdir(os.path.join(archive_dir, sub_dir))
    old_path = os.path.join(base_dir, sub_dir, data_file)
    new_path = os.path.join(archive_dir, sub_dir, data_file)
    os.rename(old_path, new_path)

def process_data_file(sub_dir, data_file):
    payload = {'client_id': sub_dir, 'file_name': data_file}
    r = requests.post("http://127.0.0.1:5000/ftp_post/{0}/{1}".format(sub_dir, data_file))
    if r.status_code == 200:
	archive_file(str(sub_dir), data_file)

def start_watcher():
   for sub_dir in os.listdir(base_dir):
       for data_file in os.listdir(os.path.join(base_dir, sub_dir)):
            process_data_file(int(sub_dir), str(data_file))

if __name__ == '__main__':
    start_watcher()
