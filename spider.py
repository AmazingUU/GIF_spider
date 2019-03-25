import os

import requests

from db_helper import DbHelper


def get_json(url):
    headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
    }
    json =requests.get(url,headers=headers).json()
    return json

def get_gif_info(json):
    if json['msg'] == 'success':
        results = json['data']['result']
        for result in results:
            gif_info = {}
            gif_info['url'] = result['gifurl']
            gif_info['label'] = result['label']
            gif_info['title'] = result['title']
            gif_info['likeNum'] = result['likeNum']
            yield gif_info
            # print(gif_info)
            # download(gif_info['title'],gif_info['url'])

def download(filename,url):
    headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
    }
    response =requests.get(url,headers=headers)
    chunk_size = 1024  # 切分数据流，一次保存数据流大小为1M，当读取到1M时保存到文件一次
    content_size = int(response.headers['content-length'])  # 数据流总大小
    if response.status_code == 200:
        print(filename + '\n文件大小:%0.2f MB' % (content_size / chunk_size / 1024))
        base_dir = os.getcwd()
        download_dir = os.path.join(base_dir, 'download')
        if not os.path.exists(download_dir):
            os.mkdir(download_dir)
        file_path = os.path.join(download_dir, filename)
        size = 0
        if not os.path.exists(file_path):
            with open(file_path + '.gif', 'wb') as f:
                for stream in response.iter_content(chunk_size=chunk_size):  # 切分数据流
                    f.write(stream)
                    size += len(stream)
                    f.flush()  # 一次write后需要flush
                    # '\r'使每一次print会覆盖前一个print信息，end=''使print不换行，如果全部保存完，print再换行
                    # 实现下载进度实时刷新，当保存到100%时，打印下一行
                    print('下载进度:%.2f%%' % float(size / content_size * 100) + '\r',
                          end='' if (size / content_size) != 1 else '\n')

if __name__ == '__main__':
    configs = {'host': 'localhost', 'user': 'root', 'password': 'admin', 'db': 'gif'}
    db = DbHelper()
    db.connenct(configs)

    try:
        last_gif = db.find_last_gif()[0]['title']
    except Exception as e:
        last_gif = None
        print('db is empty')

    url = 'https://www.soogif.com/hotGif?start=0&size=20'
    json = get_json(url)
    for gif in get_gif_info(json):
        if gif['title'] == last_gif:
            print('今日热门GIF已保存完毕')
            break
        db.save_one_data_to_hot_gif_info(gif)

    db.close()
