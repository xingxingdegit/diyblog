from flask import render_template


def home_page():
    return render_template('index.html')


def post_page(post_url):
    return render_template('post.html')


def post_content(post_url):
    pass