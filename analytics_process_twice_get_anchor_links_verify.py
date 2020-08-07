#!/usr/bin/env python

import pymysql
import yaml

config = yaml.safe_load(open('config.yaml'))

connection = pymysql.connect(host=config.get('DB_HOST'),
                             user=config.get('DB_USER'),
                             password=config.get('DB_PASS'),
                             db=config.get('DB_NAME'),
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

with connection.cursor() as cur:
    cur.execute('SELECT * FROM link')
    anchor_data = cur.fetchall()

for anchor in anchor_data:
    if anchor['link_source_page_title'] == anchor['link_target_page_title']:
        continue

    with connection.cursor() as cur:
        cur.execute('SELECT pl_from, pl_title FROM pagelinks WHERE pl_from=%s AND pl_title=%s', (anchor['link_source_page_id'], anchor['link_target_page_title']))
        data = cur.fetchall()
        missing = len(data) == 0
    
    if missing:
        print('WARNING: Missing link in pagelinks, ID %s' % anchor['link_id'])
