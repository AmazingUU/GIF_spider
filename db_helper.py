'''
数据库操作类
所需表：info
建表语句：
create table if not exists hot_gif_info(id int primary key auto_increment,title text,label varchar(50),likeNum int(5),download_url text,create_time datetime);
'''
import time

import pymysql


class DbHelper(object):
    def __init__(self):
        self.mutex = 0  # 锁信号
        self.db = None

    def connenct(self, configs):
        try:
            self.db = pymysql.connect(
                host=configs['host'],
                user=configs['user'],
                password=configs['password'],
                db=configs['db'],
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            print('db connect success')
            return self.db
        except Exception as e:
            print('db connect fail,error:', str(e))
            return None

    def close(self):
        if self.db:
            self.db.close()
            print('db close')

    def save_one_data_to_hot_gif_info(self, data):
        while self.mutex == 1:  # connetion正在被其他线程使用，需要等待
            time.sleep(1)
            print('db connect is using...')
        self.mutex = 1  # 锁定
        try:
            with self.db.cursor() as cursor:
                sql = 'insert into hot_gif_info(title,label,likeNum,download_url,create_time) values(%s,%s,%s,%s,now())'
                cursor.execute(sql, (
                data['title'], data['label'], data['likeNum'], data['url']))
                self.db.commit()
                # self.mutex = 0  # 解锁
                print('{}\t{} insert into hot_gif_info'.format(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time())),data['title']))
        except Exception as e:
            print('{}\tsave title:{} fail,error:{}'.format(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time())),data['title'], str(e)))
        finally:
            self.mutex = 0  # 解锁

    # def save_one_data_to_comment(self, data):
    #     while self.mutex == 1:  # connetion正在被其他线程使用，需要等待
    #         time.sleep(1)
    #         print('db connect is using...')
    #     self.mutex = 1  # 锁定
    #     try:
    #         with self.db.cursor() as cursor:
    #             sql = 'insert into comment(video_id,user,content,like_count,comment_time,beReplied_user,beReplied_content,beReplied_like_count,beReplied_comment_time,create_time) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,now())'
    #             cursor.execute(sql, (
    #             data['video_id'], data['user'], data['content'], data['like_count'], data['comment_time'],
    #             data['beReplied_user'], data['beReplied_content'], data['beReplied_like_count'],
    #             data['beReplied_comment_time']))
    #             self.db.commit()
    #             self.mutex = 0  # 解锁
    #             print('{}\tuser:{} comment insert into comment'.format(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time())),data['user']))
    #     except Exception as e:
    #         print('{}\tsave user:{} comment fail,error:{}'.format(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time())),data['user'], str(e)))
    #     finally:
    #         self.mutex = 0  # 解锁

    def find_last_gif(self):
        try:
            with self.db.cursor() as cursor:
                sql = 'select title from hot_gif_info where DATE_SUB(CURDATE(),INTERVAL 1 DAY) order by create_time limit 1'
                cursor.execute(sql)
                res = cursor.fetchall()
                return res
        except Exception as e:
            print('find_last_gif fail,error:', str(e))
            return None

    # def find_all_detail(self):
    #     try:
    #         with self.db.cursor() as cursor:
    #             sql = 'select url,filename from detail limit 10'
    #             cursor.execute(sql)
    #             res = cursor.fetchall()
    #             return res
    #     except Exception as e:
    #         print('find_all_detail fail,error:', str(e))
    #         return None
