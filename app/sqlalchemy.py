#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr  5 22:35:29 2019

@author: tuyuxiao
"""

import pymysql
import re
import os
import datetime
from subprocess import Popen,PIPE  
import math

class SQLAlchemy:
    TABLES = ['Blog','BlogCategory','BlogLabel','BlogLike','Category','Collection','Comment','CommentLike','Follow','User']
    def __init__(self, app):
        self.app = app
        config = self.app.config.get('SQLALCHEMY_DATABASE_URI')
        config = re.split('/|:|@',config)[-4:]
        try:
            self.db = pymysql.connect(config[2],config[0],config[1],config[3])
        except Exception as e:
            print("Fail to connect database!")
            print(e)
            os._exit(0)
        self.Model = self._inner_model_define()
        self.session = Session(self.db)
         
    def cursor(self):
        return self.db.cursor()
        
    def executeSQL(self, file):
        try:
            with open(os.path.dirname(__file__)+'/sql/'+file,'r') as f:
                sqls = f.read().replace('\n',' ').split(';')[:-1]
            cursor = self.db.cursor()
            for sql in sqls:
                cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            print(e)
    def executeSQLPopen(self, file):
        process = Popen('mysql --defaults-extra-file='+os.path.dirname(__file__)+'/sql/.config', 
                        stdout=PIPE, stdin=PIPE, shell=True)
        try:
            process.communicate(("source "+os.path.dirname(__file__)+'/sql/'+file+";").encode())
        except Exception as e:
            print(e)
        finally:
            process.terminate()
            
    def createTable(self):
        try:
            print('Creating tables...')
            self.executeSQLPopen('drop_tables.sql')
            self.executeSQLPopen('create_tables.sql')
            self.executeSQLPopen('create_triggers.sql')
        except Exception as e:
            print(e)        
    def isTableExist(self):
        try:
            cursor = self.db.cursor()
            cursor.execute("SHOW TABLES")
            return sorted([table[0] for table in cursor.fetchall()]) == self.TABLES
        except Exception as e:
            print(e)
            return False
        
    def __del__(self):
        self.db.close()
        
    def _inner_model_define(self):
        outter = self
        class Model:
            db = outter
            prime_key = []
            def __init__(self,*args,**kwargs):
                #print(self.__class__.__dict__.items())
                if args != ():
                    args = iter(args)
                    for key in self.__class__.__dict__.keys():
                        if key.startswith('_') or key[0].islower():
                            continue
                        self.__dict__[key]=next(args)
                else:
                    for key, val in self.__class__.__dict__.items():
                        if key.startswith('_') or key[0].islower():
                            continue                      
                        self.__dict__[key]=val.default
                    for key, val in kwargs.items():
                        if hasattr(self,key):
                            self.__dict__[key]=val
                        else:
                            print('Invalid attr: '+key)
            def __init_subclass__(self,*args,**kwargs):
                self.query = Query.getInstance(self)
                self.prime_key=[]
                for key, val in list(self.__dict__.items()):
                    if key.startswith('_') or key[0].islower():
                        continue
                    if val.prime_key:
                        self.prime_key.append(key)
                if len(self.prime_key) == 0:
                    print('no prime key!',self.__name__)
            def __repr__(self):
                return '<'+self.__class__.__name__+' '+str(self.__dict__[self.prime_key[0]])+'>'
            def isValid(self):
                for key, val in self.__class__.__dict__.items():
                    if key.startswith('_') or key[0].islower():
                        continue
                    if self.__getattribute__(key) is not None:
                        if not val.data_type.isValid(self.__getattribute__(key)):
                            return False
                    else:
                        if not val.nullable:
                            return False
                return True
            def __setattr__(self, name, value):
                if hasattr(self,name):
                    data_type = self.__class__.__dict__.get(name).data_type
                    if data_type.isValid(value):
                        self.__dict__[name] = value
                        if len(self.prime_key) > 0:
                            sql = "UPDATE " + self.__class__.__name__ + " SET "
                            sql += name + " = " + data_type.getValue(value) + " WHERE "
                            for prime_key in self.prime_key:
                                sql += prime_key+" = "+str(self.__dict__[prime_key])+" AND "
                            self.execute(sql[:-4])
                
            def insertSQL(self):
                sql = "INSERT INTO " + self.__class__.__name__
                keys = " ("
                values = " ("
                for key, val in self.__class__.__dict__.items():
                    if key.startswith('_') or key[0].islower():
                        continue
                    if self.__getattribute__(key) is not None:
                        keys += key + ","
                        values += val.data_type.getValue(self.__getattribute__(key)) + ","
                return sql+keys[:-1]+") VALUES"+values[:-1]+")"
            def deleteSQL(self):
                sql = "DELETE FROM " + self.__class__.__name__ + " WHERE "
                if self.__class__.__dict__.get(self.prime_key[0]) is not None:
                    for prime_key in self.prime_key:
                        sql += prime_key+" = "+str(self.__dict__[prime_key])+" AND "
                    return sql[:-4]
                else:
                    for key, val in self.__class__.__dict__.items():
                        if key.startswith('_') or key[0].islower():
                            continue
                        if self.__getattribute__(key) is not None:
                            sql += " " + key + "=" + val.data_type.getValue(self.__getattribute__(key)) + " AND"
                return sql[:-4]
            def execute(self,sql):
                cursor = self.cursor()
                cursor.execute(sql)
            def cursor(self):
                return self.db.cursor()
        return Model
    
    class Column:
        def __init__(self,data_type,prime_key=False,unique=False,nullable=False,default=None):
            self.data_type = data_type
            self.prime_key = prime_key
            self.unique = unique
            self.nullable = nullable
            self.default = default
            
    class Integer:
        def isValid(data):
            if data is None:
                return True
            return isinstance(data,int)
        def getValue(data):
            if data is None:
                return 'null'
            return str(data)
        
    class String:
        def __init__(self, max_length):
            self.max_length = max_length
        def isValid(self, data):
            if data is None:
                return True
            if isinstance(data,str):
                if len(data) <= self.max_length:
                    return True
            return False
        def getValue(self,data):
            if data is None:
                return 'null'
            return "'"+str(data)+"'"
        
    class TimeStamp:
        def isValid(data):
            if data is None:
                return True
            return isinstance(data,datetime.datetime)
        def getValue(data):
            if data is None:
                return 'null'
            return "'"+str(data)+"'"
        
class Query:
    INSTANCES = {}
    @staticmethod
    def getInstance(model):
        if not Query.INSTANCES.get(model.__name__):
            Query.INSTANCES[model.__name__] = Query(model)
        return Query.INSTANCES.get(model.__name__)
    def __init__(self, model):
        self.tableName = model.__name__
        self.model = model
        self.suffix = ""
    def execute(self, sql):
        try:
            cursor = self.model.db.cursor()
            cursor.execute(sql+self.suffix)
            return cursor.fetchall()
        except Exception as e:
            print(e)
            return ()
        finally:
            self.suffix = ""
    def all(self,count=False):
        if count:
            res = self.execute("SELECT COUNT(*) FROM " + self.tableName)
            return res[0][0]
        else:
            res = self.execute("SELECT * FROM "+self.tableName)
            return [self.model(*args) for args in res]
    def get(self, pid):
        if len(self.model.prime_key) == 0:
            print('Model has no specific prime key!')
            return ()
        res = self.execute("SELECT * FROM "+self.tableName+" WHERE "+ self.model.prime_key[0]+" = "+str(pid))
        if res == ():
            return None
        else:
            return self.model(*res[0])
    def filter_by(self, count=False,**kwargs): 
        cond = ""
        for key,val in kwargs.items():
            cond += key + " = '" + str(val) + "' AND "
        if count:
            res = self.execute("SELECT COUNT(*) FROM " + self.tableName + " WHERE "+cond[:-4])
            return res[0][0]
        else:
            res = self.execute("SELECT * FROM " + self.tableName + " WHERE "+cond[:-4])
            return [self.model(*args) for args in res]
    def filter(self):
        pass
    def limit(self, n):
        self.suffix += " LIMIT "+str(n)+" "
        return self
    def offset(self, n):
        self.suffix += " OFFSET "+str(n)+" "
        return self
    def paginate(self, page, per_page,**kwargs):
        temp = self.suffix
        self.suffix = ""
        if len(kwargs.keys())>0:
            total = self.filter_by(count=True,**kwargs)
        else:
            total = self.all(count=True)
        if total == 0:
            return Pagination([], 0, 0)
        total_page = math.ceil(total/per_page)
        if page > total_page:
            page = total_page
        if page < 1:
            page = total_page
        self.suffix = temp
        self.limit(per_page)
        self.offset((page-1)*per_page)
        if len(kwargs.keys())>0:
            res = self.filter_by(**kwargs)
        else:
            res = self.all()
        return Pagination(res, page, total_page)
    def paginate_in(self, page, per_page, name, values,**kwargs):
        temp = self.suffix
        self.suffix = ""
        cond = ""
        for key,val in kwargs.items():
            cond += key + " = '" + str(val) + "' AND "
        total = self.execute("SELECT COUNT(*) FROM "+self.tableName+" WHERE "+cond+name+" IN ("+str(values)[1:-1]+")")[0][0]
        if total == 0:
            return Pagination([], 0, 0)
        total_page = math.ceil(total/per_page)
        if page > total_page:
            page = total_page
        if page < 1:
            page = total_page
        self.suffix = temp
        self.limit(per_page)
        self.offset((page-1)*per_page)
        res = self.execute("SELECT * FROM "+self.tableName+" WHERE "+cond+name+" IN ("+str(values)[1:-1]+")")
        return Pagination([self.model(*args) for args in res], page, total_page)
        
    def order_by(self, name, desc=False):
        self.suffix += " ORDER BY "+name+" "
        if desc:
            self.suffix += " DESC "
        return self
    
class Pagination:
    def __init__(self, models, page, total_page):
        self.items = models
        self.page = page
        self.prev_num = page-1
        self.next_num = page+1
        self.has_prev = self.prev_num >= 1
        self.has_next = self.next_num <= total_page
    
class Session:
    def __init__(self, db):
        self.db = db
    def insert(self, sql):
        try:
            cursor = self.db.cursor()
            cursor.execute(sql)
            return True
        except Exception as e:
            print(e)
            #self.db.rollback()
            return False
    def add(self, model):
        if model.isValid():
            return self.insert(model.insertSQL())
        else:
            return False
    def delete(self, model):
        try:
            cursor = self.db.cursor()
            cursor.execute(model.deleteSQL())
            return True
        except Exception as e:
            print(e)
            #self.db.rollback()
            return False
    def commit(self):
        self.db.commit()