from api.dbpool import with_db
from flask import g
import os
from hashlib import sha256
import logging
import traceback
import datetime

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
        set_data.append({'key': 'install_init', 'value': 1, 'status': 2, 'intro': '1表示已经初始化过了'})
        set_data.append({'key': 'sitename', 'value': sitename, 'intro': '网站名称'})
        set_data.append({'key': 'admin_url', 'value': admin_url, 'intro': '后台登录地址'})
        set_data.append({'key': 'avatar_url', 'value': 'static/image/123.jpg', 'intro': '头像路径'})
        set_data.append({'key': 'footer_info', 'value': '<p>hello world</p>', 'intro': '页脚信息'})
        set_data.append({'key': 'login_prefix_key_timeout', 'value': 300, 
                     'intro': '登录界面获取的安全key超时时间， 这个key与用户名密码共同组成登录验证。'})
        set_data.append({'key': 'user_timeout', 'value': 36000, 'intro': '用户登陆以后空闲的超时时间，超时以后需要重新登陆'})
        set_data.append({'key': 'del_number', 'value': 10, 'intro': '可以一次性删除的记录数目'})
        set_data.append({'key': 'login_blacklist_timeout', 'value': 600, 'intro': '登录黑名单的封锁时间,秒'})
        set_data.append({'key': 'login_fail_count', 'value': 10, 'intro': '连续登录失败10次，进登录黑名单'})
        set_data.append({'key': 'login_fail_lasttime', 'value': 60, 'intro': '在没有进黑名单的情况下，超过这个时间的登录会清零登录失败计数，秒'})
        set_data.append({'key': 'upload_file_size', 'value': 10000000, 'intro': '单位Byte'})
        set_data.append({'key': 'upload_file_ext', 'value': 'png,jpg,jpeg,gif,txt,tar,zip', 'intro': '允许上传的扩展名, 逗号分隔'})
        set_data.append({'key': 'upload_file_mime', 'value': 'image,text,application', 'intro': '允许上传的mime主类型。逗号分隔'})
        set_state = g.db.insert('setting', set_data)

        class_data = []
        class_data.append({'id': 1, 'classname': 'unclass', 'status': 2, 'sort': 0, 'intro': '未分类'})
        class_state = g.db.insert('class', class_data)

        notice_data = []
        timestamp = int(datetime.datetime.now().timestamp())
        notice_data.append({'id': 1, 'content': '', 'uptime': timestamp, 'type': 1, 'status': 1, 'intro': '静态公告占位'})
        notice_state = g.db.insert('notice', notice_data)

        if set_state[0] and class_state[0] and notice_state[0]:
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
                `class` tinyint(3) unsigned DEFAULT 1,
                `tags` varchar(20) DEFAULT '0',
                `status` tinyint(3) unsigned DEFAULT 2 COMMENT '文章状态，1已发布，2草稿，3已删除',
                `visits` int(10) unsigned DEFAULT 0,
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
                `status` tinyint(4) DEFAULT 1 COMMENT '是否在主页显示，1显示，2不显示',
                `sort` tinyint(4) DEFAULT 1 COMMENT '在主页展示时的排列顺序',
                `intro` varchar(100) DEFAULT NULL,
                PRIMARY KEY (`id`)
              ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
              '''
    tags_sql = r'''
              CREATE TABLE IF NOT EXISTS `tags` (
                `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
                `tagname` varchar(100) NOT NULL unique,
                `intro` varchar(100) DEFAULT NULL,
                `status` tinyint(4) DEFAULT 1 COMMENT '是否在主页显示，1显示，2不显示',
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
              `status` tinyint(4) DEFAULT 1 COMMENT '1正常， 2不可修改',
              `intro` VARCHAR(100) DEFAULT NULL,
              PRIMARY KEY (`id`),
              UNIQUE KEY `key` (`key`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
            '''
    attach_sql = r'''
              CREATE TABLE IF NOT EXISTS `attach` (
              `id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
              `filename` VARCHAR(70) NOT NULL UNIQUE COMMENT '文件名称',
              `pathname` VARCHAR(100) NOT NULL COMMENT '在系统上的存放路径,同时也是对外的路径，包含文件名称',
              `mimetype` VARCHAR(50) NOT NULL,
              `size` int(10) UNSIGNED NOT NULL COMMENT '文件大小',
              `width` int(10) UNSIGNED DEFAULT '0' COMMENT '图片宽度',
              `height` int(10) UNSIGNED DEFAULT '0' COMMENT '图片高度',
              `uptime` int(10) UNSIGNED NOT NULL,
              `private` tinyint(4) DEFAULT 1 COMMENT '1公开的， 2私有的',
              `is_image` tinyint(4) DEFAULT 1 COMMENT '1是图片，2不是',
              `status` tinyint(4) DEFAULT 1 COMMENT '1正常，2已删除',
              `intro` VARCHAR(100) DEFAULT NULL,
              PRIMARY KEY (`id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
            '''

    # 如果添加聊天的功能， 聊天信息不存储， 只路由。
    notice_sql = r'''
              CREATE TABLE IF NOT EXISTS `notice` (
              `id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
              `title` VARCHAR(70) DEFAULT '' COMMENT '标题',
              `content` VARCHAR(100) NOT NULL COMMENT '内容',
              `uptime` int(10) UNSIGNED NOT NULL,
              `type` tinyint(4) DEFAULT 1 COMMENT '1静态公告，2动态公告, 3用户留言板',
              `status` tinyint(4) DEFAULT 1 COMMENT '1有效, 2无效',
              `intro` VARCHAR(100) DEFAULT NULL,
              PRIMARY KEY (`id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
            '''


    p = g.db.query(posts_sql)
    c = g.db.query(class_sql)
    t = g.db.query(tags_sql)
    u = g.db.query(users_sql)
    s = g.db.query(setting_sql)
    a = g.db.query(attach_sql)
    n = g.db.query(notice_sql)
    if p[0] and c[0] and t[0] and u[0] and s[0] and a[0] and n[0]:
        return True
    else:
        return False
