#!/usr/bin/env python

import pymysql
import requests
import yaml
import mwxml
import mwparserfromhell
import re
import html
import urllib.parse

config = yaml.safe_load(open('config.yaml'))
LIMIT = None
DOMAIN = "cs.wikipedia.org"

dump = mwxml.Dump.from_file(open("cswiki-latest-pages-articles-multistream.xml"))
RE_ANCHOR = re.compile(r'([^#]*)#(.*)')
RE_INTERWIKI = re.compile(r'^([a-zA-Z]+):.*')

connection = pymysql.connect(host=config.get('DB_HOST'),
                             user=config.get('DB_USER'),
                             password=config.get('DB_PASS'),
                             db=config.get('DB_NAME'),
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

def normalize_page_title(title):
    tmp = title.replace(' ', '_')
    return tmp[0].upper() + tmp[1:]

# get interwiki map
r = requests.get("https://%s/w/api.php" % DOMAIN, params={
	"action": "query",
	"format": "json",
	"meta": "siteinfo",
	"siprop": "interwikimap"
})
interwiki_map = {}
data = r.json().get('query').get('interwikimap')
for entry in data:
    interwiki_map[entry["prefix"]] = entry["url"]

# cleanup
with connection.cursor() as cur:
    cur.execute('TRUNCATE TABLE page;') # TODO: Make this actually not truncate

with connection.cursor() as cur:
    cur.execute('TRUNCATE TABLE link;')

connection.commit()


i = 0
for linking_page in dump.pages:
    # Sanity: Exclude non-mainpage pages
    if linking_page.namespace != 0:
        continue
    
    # Exclude the main page
    if linking_page.title == "Hlavní strana":
        continue
        
    i += 1
    if LIMIT is not None and i > LIMIT:
        break

    revision = next(linking_page) # only current revision should be here

    with connection.cursor() as cur:
        cur.execute('INSERT INTO page(page_id, page_title) VALUES (%s, %s)', (linking_page.id, linking_page.title))
    connection.commit()

    try:
        parsed = mwparserfromhell.parse(revision.text)
    except:
        with connection.cursor() as cur:
            cur.execute('UPDATE page SET page_link_processed=false WHERE page_id=%s', (linking_page.id, ))
        connection.commit()
        continue

    for link in parsed.filter_wikilinks():
        # get link title in expectable form
        link_title = html.unescape(urllib.parse.unquote(str(link.title)))

        # detect interwiki link
        m = RE_INTERWIKI.search(link_title)
        if m is not None:
            prefix = m.group(1)
            if prefix.lower() in interwiki_map:
                continue # skip interwiki link


        # process link
        m = RE_ANCHOR.search(link_title)

        if m is not None:
            linked_page_title = m.group(1).strip()
            linked_anchor = m.group(2).strip()
        else:
            continue # comment out if you want no anchor links to be included too
            linked_page_title = str(link.title)
            linked_anchor = None
        
        if linked_page_title == '':
            linked_page_title = linking_page.title

        with connection.cursor() as cur:
            cur.execute(
                '''
                INSERT INTO link(link_source_page_id, link_source_page_title, link_target_page_title, link_anchor)
                VALUES (%s, %s, %s, %s)
                ''',
                (linking_page.id, normalize_page_title(linking_page.title), normalize_page_title(linked_page_title), linked_anchor)
            )
            connection.commit()
