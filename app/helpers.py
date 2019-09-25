from flask import current_app
from threading import Thread
import boto3
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from collections import namedtuple

Team = namedtuple('Team', ['name', 'played', 'win', 'loss', 'g_for', 'g_against', 'pm', 'points'])

def upload_file_s3(file, bucket_name, acl='public-read', folder=None):

    s3 = boto3.client(
       's3',
       aws_access_key_id=current_app.config['S3_KEY'],
       aws_secret_access_key=current_app.config['S3_SECRET'],
       region_name=current_app.config['AWS_DEFAULT_REGION'])

    if folder:
        filename = folder+'/'+file.filename
    else:
        filename = file.filename

    try:
        s3.upload_fileobj(
            file,
            bucket_name,
            filename,
            ExtraArgs={
                'ACL': acl,
                'ContentType': file.content_type})

    except Exception as e:
        print('Failure during upload: ', e)
        return None

    return '{}{}'.format(current_app.config['S3_LOCATION'], filename)


def delete_file_s3(bucket_name, key):

    s3 = boto3.client(
       's3',
       aws_access_key_id=current_app.config['S3_KEY'],
       aws_secret_access_key=current_app.config['S3_SECRET'],
       region_name=current_app.config['AWS_DEFAULT_REGION'])

    try:
        s3.delete_object(Bucket=bucket_name, Key=key)
    except Exception as e:
        print('Failure during delete: ', e)
        return None

    return '{}{}'.format(current_app.config['S3_LOCATION'], key)


def url_parse_s3(url):
    o = urlparse(url)
    key = o.path[1:]
    bucket = o.netloc.split('.',1)[0]

    return bucket, key


def scrape_standings_table():
    url = 'http://www.sentex.net/~pmartin/2019-2020/results.htm#Standings'
    pr = requests.get(url, timeout=10)
    soup = BeautifulSoup(pr.content, 'lxml')
    start = soup.find_all('a', {'name':'Standings'})[0]
    table = start.find_next('table')

    teams = []
    for row in table.find_all('tr')[1:]:
        data = row.find_all('td')
        team = Team(*[d.string for d in data])
        teams.append(team)

    return teams
