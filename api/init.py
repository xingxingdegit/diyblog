from api.dbpool import with_db
from flask import g
import os
from hashlib import sha256
import logging
import traceback

log = logging.getLogger(__name__)

@with_db('write')
def create_user(data):
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    phone = data.get('phone', '').strip()
    email = data.get('email', '').strip()
    intro = data.get('intro', '').strip()
    cookie_key = data['cookie_key']
    if not (username and password):
        return False

    sha256_password = sha256(password.encode('utf-8')).hexdigest()
    data = {'username': username, 'password': sha256_password, 'cookie_key': cookie_key}
    if phone:
        data['phone'] = phone
    if email:
        data['email'] = email
    if intro:
        data['intro'] = intro

    state = g.db.insert('users', data)
    if state[0]:
        return True
    return False

@with_db('write')
def init_setting(data):
    try:
        set_data = []
        sitename = data.get('sitename', '').strip()
        admin_url = data.get('admin_url', 'admin_back').strip()
        set_data.append({'key': 'install_init', 'value': 1, 'intro': '1表示已经初始化过了'})
        set_data.append({'key': 'sitename', 'value': sitename, 'intro': '昵称'})
        set_data.append({'key': 'admin_url', 'value': admin_url, 'intro': '后台登录地址'})
        set_data.append({'key': 'avatar_url', 'value': 'static/image/123.jpg', 'intro': '头像路径'})
        set_data.append({'key': 'login_prefix_key_timeout', 'value': 300, 
                     'intro': '登录界面获取的安全key超时时间， 这个key与用户名密码共同组成登录验证。'})
        set_data.append({'key': 'user_timeout', 'value': 36000, 'intro': '用户登陆以后空闲的超时时间，超时以后需要重新登陆'})
        set_data.append({'key': 'del_number', 'value': 10, 'intro': '可以一次性删除的记录数目'})
        set_data.append({'key': 'login_blacklist_timeout', 'value': 600, 'intro': '登录黑名单的封锁时间,秒'})
        set_data.append({'key': 'login_fail_count', 'value': 10, 'intro': '连续登录失败10次，进登录黑名单'})
        set_data.append({'key': 'login_fail_lasttime', 'value': 60, 'intro': '在没有进黑名单的情况下，超过这个时间的登录会清零登录失败计数，秒'})
        state = g.db.insert('setting', set_data)
        if state[0]:
            return True
        return False
    except Exception:
        log.error(traceback.format_exc())
        return False

   
# 初始化表
@with_db('write')
def create_table():
    # status, 1 已发布， 2 草稿， 3 已删除
    posts_sql = r'''
                CREATE TABLE IF NOT EXISTS `posts` (
                `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
                `title` varchar(100) NOT NULL unique,
                `create_time` int(10) unsigned NOT NULL,
                `update_time` int(10) unsigned NOT NULL,
                `summary` varchar(200) DEFAULT NULL,
                `posts` text DEFAULT NULL,
                `code_style` varchar(50),
                `class` tinyint(3) unsigned DEFAULT NULL,
                `status` tinyint(3) unsigned NOT NULL,
                `visits` int(10) unsigned DEFAULT NULL,
                `url` varchar(100) unique,
                `istop` tinyint(4) DEFAULT NULL,
                `intro` varchar(100) DEFAULT NULL,
                PRIMARY KEY (`id`)
              ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
              '''
    class_sql = r'''
                CREATE TABLE IF NOT EXISTS `class` (
                `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
                `classname` varchar(100) NOT NULL unique,
                `status` tinyint(4) NOT NULL,
                `intro` varchar(100) DEFAULT NULL,
                PRIMARY KEY (`id`)
              ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
              '''
    tags_sql = r'''
              CREATE TABLE IF NOT EXISTS `tags` (
                `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
                `tagname` varchar(100) NOT NULL unique,
                `post` int(10) unsigned NOT NULL,
                `intro` varchar(100) DEFAULT NULL,
                PRIMARY KEY (`id`)
              ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
              '''
    users_sql = r'''
              CREATE TABLE IF NOT EXISTS `users` (
              `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
              `username` varchar(100) NOT NULL,
              `password` varchar(100) NOT NULL,
              `phone` varchar(20) DEFAULT NULL COMMENT '电话',
              `email` varchar(50) DEFAULT NULL COMMENT '邮件',
              `cookie_key` varchar(50) DEFAULT NULL COMMENT '加密cookie的key',
              `intro` varchar(100) DEFAULT NULL,
              PRIMARY KEY (`id`),
              UNIQUE KEY `username` (`username`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
            '''
    setting_sql = r'''
              CREATE TABLE IF NOT EXISTS `setting` (
              `id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
              `key` VARCHAR(50) NOT NULL COMMENT '设置项',
              `value` VARCHAR(50) NOT NULL,
              `intro` VARCHAR(100) DEFAULT NULL,
              PRIMARY KEY (`id`),
              UNIQUE KEY `key` (`key`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
            '''

    p = g.db.query(posts_sql)
    c = g.db.query(class_sql)
    t = g.db.query(tags_sql)
    u = g.db.query(users_sql)
    s = g.db.query(setting_sql)
    if p[0] and c[0] and t[0] and u[0] and s[0]:
        return True
    else:
        return False