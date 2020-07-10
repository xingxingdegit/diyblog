from api.dbpool import with_db
from flask import g
from hashlib import sha256

@with_db('write')
def create_user(username, password):
    sha256_password = sha256(password.encode('utf-8')).hexdigest()
    data = {'username': username, 'password': sha256_password}
    state = g.db.insert('users', data)
    if state[0]:
        return True
    return False
   
# 初始化表
@with_db('write')
def create_table():
    posts_sql = r'''
                CREATE TABLE IF NOT EXISTS `posts` (
                `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
                `title` varchar(100) NOT NULL unique,
                `create_time` int(10) unsigned NOT NULL,
                `update_time` int(10) unsigned NOT NULL,
                `posts` longtext DEFAULT NULL,
                `class` tinyint(3) unsigned DEFAULT NULL,
                `status` tinyint(3) unsigned NOT NULL,
                `visits` int(10) unsigned DEFAULT NULL,
                `urls` varchar(100) DEFAULT NULL unique,
                `istop` tinyint(4) DEFAULT NULL,
                PRIMARY KEY (`id`)
              ) ENGINE=InnoDB DEFAULT CHARSET=utf8
              '''
    class_sql = r'''
                CREATE TABLE IF NOT EXISTS `class` (
                `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
                `classname` varchar(100) NOT NULL unique,
                `status` tinyint(4) NOT NULL,
                PRIMARY KEY (`id`)
              ) ENGINE=InnoDB DEFAULT CHARSET=utf8
              '''
    tags_sql = r'''
              CREATE TABLE IF NOT EXISTS `tags` (
                `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
                `tagname` varchar(100) NOT NULL unique,
                `post` int(10) unsigned NOT NULL,
                PRIMARY KEY (`id`)
              ) ENGINE=InnoDB DEFAULT CHARSET=utf8
              '''
    users_sql = r'''
                CREATE TABLE IF NOT EXISTS `users` (
                `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
                `username` varchar(100) NOT NULL unique,
                `password` varchar(100) NOT NULL,
                PRIMARY KEY (`id`)
              ) ENGINE=InnoDB DEFAULT CHARSET=utf8
              '''

    p = g.db.query(posts_sql)
    c = g.db.query(class_sql)
    t = g.db.query(tags_sql)
    u = g.db.query(users_sql)
    if p[0] and c[0] and t[0] and u[0]:
        return True
    else:
        return False