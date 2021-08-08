import requests
from bs4 import BeautifulSoup
import g_fetcher
import time
import random
import os

def generate_file_url_list():
    lofi_src_url = 'https://lofirecords.com/blogs/releases/'
    lofi_base_url = 'https://lofirecords.com'

    print('Accessing Lofi Records webpage... ', end='\r')

    reqs = requests.get(lofi_src_url)
    soup = BeautifulSoup(reqs.text, 'html.parser')

    print('Accessing Lofi Records webpage... done')

    lofi_page_urls = []

    print('Finding web urls of all releases... ', end='\r')

    for link in soup.find_all('a'):
        if '/blogs/releases/' in str(link.get('href')):
            lofi_page_urls.append(lofi_base_url + str(link.get('href')))

    lofi_page_urls = list(set(lofi_page_urls))

    print(f'Finding web urls of all releases... done, total count: {len(lofi_page_urls)} ')

    lofi_file_page_urls = []

    print('\nFinding web urls of file download pages... ', end='\r')

    lofi_file_page_list = "lofi_download_url_list.txt"
    lofi_file_page_list_small = "lofi_download_url_list_small.txt"
    open(lofi_file_page_list, "w").close()
    open(lofi_file_page_list_small, "w").close()

    for lofi_page_url in lofi_page_urls:
        reqs = requests.get(lofi_page_url)
        soup = BeautifulSoup(reqs.text, 'html.parser')
        for link in soup.find_all('a'):
            if 'bit.ly' in str(link.get('href')) or 'drive.google.com' in str(link.get('href')):
                if 'drive.google.com' in str(link.get('href')):
                    drive_url_temp = str(link.get('href'))
                else:
                    drive_url_temp = requests.Session().head(str(link.get('href')), allow_redirects=True).url
                if 'googleusercontent.com' in drive_url_temp:
                    with open(lofi_file_page_list_small, "a") as out_list:
                        out_list.write(str(link.get('href')) + '\n')
                        out_list.close()
                else: 
                    with open(lofi_file_page_list, "a") as out_list:
                        out_list.write(drive_url_temp + '\n')
                        out_list.close()
                lofi_file_page_urls.append(drive_url_temp)
                print(f'Finding web urls of file download pages... progress: {len(lofi_file_page_urls)}', end='\r')
        time.sleep(random.randint(8, 12))

    print(f'Finding web urls of file download pages... done, total count: {len(lofi_file_page_urls)}')

def fetch_files_from_drive():
    progress = 0
    with open(os.path.dirname(__file__) + '/lofi_download_url_list.txt', 'r') as f:
        lines = f.readlines()
    for line in lines:
        print(f'Downloading large files {progress}/{len(lines)}... ', end='\r')
        id = line.split('id=', 1)[1].split('\n', 1)[0]
        try:
            g_fetcher.download_file_from_google_drive(id, f'{os.path.dirname(__file__)}/{id}.zip')
            progress += 1
        except Exception as e:
            print(str(e))
    print(f'Download completed. Total large files downloaded: {progress}/{len(lines)} ')

    print()
    progress = 0
    with open(os.path.dirname(__file__) + '/lofi_download_url_list_small.txt', 'r') as f:
        lines = f.readlines()
    for line in lines:
        print(f'Downloading small files {progress}/{len(lines)}... ', end='\r')
        try:
            open(f'{progress + 1}_small.zip', 'wb').write(requests.get(line.split('\n', 1)[0], allow_redirects=True).content)
            progress += 1
        except Exception as e:
            print(str(e))
    print(f'Download completed. Total small files downloaded: {progress}/{len(lines)} ')

if(input('[y]es to clear the existing url list and recreate it. \nNote that this may take quite some time to avoid reCAPTCHA: ') == 'y'):
    print()
    generate_file_url_list()
    print()
    fetch_files_from_drive()
else: 
    if(input('\n[y]es to fetch files from existing url list: ') == 'y'):
        print()
        fetch_files_from_drive()