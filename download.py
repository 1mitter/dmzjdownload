# -*- coding: utf-8 -*-
import requests
import time
import os
from retrying import retry
from pyquery import PyQuery as pq
import sys
import re

def get_chapters():
    requests_to_chapters = safe_requests('http://v3api.dmzj.com/comic/comic_' + comic_id + '.json?channel=Android&version=2.7.013&timestamp=' + str(int(time.time())))
    chapters = requests_to_chapters.json()['chapters'][0]['data']
    return chapters

def get_pages(chapters):
    for chapter in chapters:
        if os.path.exists(os.path.join(base_path, re.sub(r'[/:*?"<>|]', '', chapter['chapter_title']))):
            os.chdir(os.path.join(base_path, re.sub(r'[/:*?"<>|]', '', chapter['chapter_title'])))
        else:
            os.mkdir(os.path.join(base_path, re.sub(r'[/:*?"<>|]', '', chapter['chapter_title'])))
            os.chdir(os.path.join(base_path, re.sub(r'[/:*?"<>|]', '', chapter['chapter_title'])))
        requests_to_pages = safe_requests('http://v3api.dmzj.com/chapter/' + comic_id + '/' + str(chapter['chapter_id']) +'.json?channel=Android&version=2.7.013&timestamp='+ str(int(time.time())))
        pages = requests_to_pages.json()['page_url']
        download_imgs(pages)
        print(chapter['chapter_title'] + 'download done')

def download_imgs(pages):
    for page in pages:
        download_img = safe_requests(page, True)
        with open(page.split('/')[-1], 'wb') as f:
            for chunk in download_img.iter_content(chunk_size = 128):
                f.write(chunk)

@retry(stop_max_attempt_number = 50, wait_fixed = 5000)
def safe_requests(url, streamflag = False):
    data = requests.get(url, headers = headers, stream = streamflag)
    assert data.status_code == 200 or data.status_code == 404
    return data


base_path = sys.argv[2]

headers = {
    'Referer': 'http://images.dmzj.com/'
}

r = requests.get(sys.argv[1])
html = pq(r.text)
comic_id_node = html('#comic_id')
comic_id = str(comic_id_node.html())

chapters = get_chapters()
get_pages(chapters)