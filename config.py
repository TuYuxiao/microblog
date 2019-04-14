#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr  5 23:09:26 2019

@author: tuyuxiao
"""

class Config(object):
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:19990114tyx@localhost/microblog"
    CSRF_ENABLED = True
    SECRET_KEY = 'micro-blog'