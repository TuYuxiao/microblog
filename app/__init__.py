#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr  5 22:17:22 2019

@author: tuyuxiao
"""

from flask import Flask
from config import Config
from app.sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object(Config)

lm = LoginManager(app)
db = SQLAlchemy(app)
#db.createTable()
from app.faker_data import generateData
#generateData(20,5,40)

from app import routes