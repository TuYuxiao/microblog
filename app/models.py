#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr  5 22:27:55 2019

@author: tuyuxiao
"""

from app import db
from app import lm
from flask_login import UserMixin
import hashlib
from faker import Faker
from numpy.random import randint

faker = Faker()

class User(UserMixin, db.Model):
    UserID = db.Column(db.Integer,prime_key=True,nullable=True)
    UserName = db.Column(db.String(20))
    UserPasswd = db.Column(db.String(32))
    UserEmail = db.Column(db.String(32),unique=True)
    UserRole = db.Column(db.Integer,nullable=True)
    UserSelfDescription = db.Column(db.String(200),nullable=True)
    UserAge = db.Column(db.Integer,nullable=True)
    RegistrationTime = db.Column(db.TimeStamp,nullable=True)
    LastLoginTime = db.Column(db.TimeStamp,nullable=True)
    Avator = db.Column(db.String(5000),nullable=True)
    
    def get_id(self):
        return self.__dict__.get(self.prime_key)
    def set_passwd(self, passwd):
        self.__setattr__('UserPasswd',self.md5(passwd))
    def check_passwd(self, passwd):
        return self.__getattribute__('UserPasswd') == self.md5(passwd)
    @staticmethod
    def md5(passwd):
        return hashlib.md5(passwd.encode()).hexdigest()
    @staticmethod
    def fake(num):
        for i in range(num):
            user = User(UserName=faker.name(),UserPasswd=hashlib.md5('123456'.encode()).hexdigest(),
                        UserEmail=faker.email(),UserSelfDescription=faker.paragraph(),
                        RegistrationTime=faker.date_time_this_year())
            db.session.add(user)
        db.session.commit()
                                     
class Blog(db.Model):
    BlogID = db.Column(db.Integer,prime_key=True,nullable=True)
    PublishDate = db.Column(db.TimeStamp,nullable=True)
    LastEditTime = db.Column(db.TimeStamp,nullable=True)
    BlogTitle = db.Column(db.String(30))
    BlogContent = db.Column(db.String(5000))
    PageViews = db.Column(db.Integer,default=0)
    PublisherID = db.Column(db.Integer)
    
    @staticmethod
    def fake(num,numUser):
        for i in range(num):
            blog = Blog(BlogTitle=faker.sentence()[:30],BlogContent=faker.paragraph(80),
                        PublisherID=randint(1,numUser+1),
                        PublishDate=faker.date_time_this_month())
            db.session.add(blog)
        db.session.commit()

class Comment(db.Model):
    CommentID = db.Column(db.Integer,prime_key=True,nullable=True)
    CommentDate = db.Column(db.TimeStamp,nullable=True)
    CommentContent = db.Column(db.String(300))
    BlogID = db.Column(db.Integer,nullable=True)
    CommenterID = db.Column(db.Integer)
    FatherCommentID = db.Column(db.Integer,nullable=True)
    
    @staticmethod
    def fake(numBlog,numUser):
        for i in range(numBlog*3):
            comment = Comment(CommentContent = faker.paragraph(2),BlogID = randint(1,numBlog+1),CommenterID = randint(1,numUser+1))
            db.session.add(comment)
        for i in range(numBlog*5):
            comment = Comment(CommentContent = faker.paragraph(2),CommenterID = randint(1,numUser+1),FatherCommentID=randint(1,numBlog*3+1))
            db.session.add(comment)
        db.session.commit()
    
class Category(db.Model):
    CategoryID = db.Column(db.Integer,prime_key=True,nullable=True)
    CategoryName = db.Column(db.String(20))
    CategoryDescription = db.Column(db.String(50),nullable=True)
    FatherCategoryID = db.Column(db.Integer,nullable=True)
    
    @staticmethod
    def fake(num):
        for i in range(num):
            category = Category(CategoryName = faker.word()[:20],
                                CategoryDescription = faker.sentence()[:50])
            db.session.add(category)
        for i in range(2*num):
            category = Category(CategoryName = faker.word()[:20],
                                CategoryDescription = faker.sentence()[:50],FatherCategoryID=randint(1,num+1))
            db.session.add(category)
        for i in range(2*num):
            category = Category(CategoryName = faker.word()[:20],
                                CategoryDescription = faker.sentence()[:50],FatherCategoryID=randint(1,3*num+1))
            db.session.add(category)
        db.session.commit()
    
class BlogLabel(db.Model):
    BlogID = db.Column(db.Integer,prime_key=True)
    LabelName = db.Column(db.String(20),prime_key=True)
    
    @staticmethod
    def fake(numBlog):
        for i in range(numBlog*3):
            blogLabel = BlogLabel(BlogID = randint(1,numBlog+1),LabelName = faker.word())
            db.session.add(blogLabel)
        db.session.commit()
        
class BlogCategory(db.Model):
    BlogID = db.Column(db.Integer,prime_key=True)
    CategoryID = db.Column(db.Integer,prime_key=True)
    
    @staticmethod
    def fake(numBlog,numCategory):
        for i in range(numBlog*3):
            blogCategory = BlogCategory(BlogID = randint(1,numBlog+1),CategoryID = randint(1,numCategory+1))
            db.session.add(blogCategory)
        db.session.commit()
        
class Follow(db.Model):
    FollowerID = db.Column(db.Integer,prime_key=True)
    BeFollowedID = db.Column(db.Integer,prime_key=True)
    
    @staticmethod
    def fake(numUser):
        for i in range(numUser**2//4):
            follow = Follow(FollowerID=randint(1,numUser+1),BeFollowedID=randint(1,numUser+1))
            db.session.add(follow)
        db.session.commit()
        
class BlogLike(db.Model):
    UserID = db.Column(db.Integer,prime_key=True)
    BlogID = db.Column(db.Integer,prime_key=True)
    LikeTime = db.Column(db.TimeStamp,nullable=True)
    
    @staticmethod
    def fake(num,numUser,numBlog):
        for i in range(num):
            blogLike = BlogLike(UserID = randint(1,numUser+1),BlogID = randint(1,numBlog+1))
            db.session.add(blogLike)
        db.session.commit()
        
class CommentLike(db.Model):
    UserID = db.Column(db.Integer,prime_key=True)
    CommentID = db.Column(db.Integer,prime_key=True)
    LikeTime = db.Column(db.TimeStamp,nullable=True)
    
    @staticmethod
    def fake(num,numUser,numComment):
        for i in range(num):
            commentLike = CommentLike(UserID = randint(1,numUser+1),CommentID = randint(1,numComment+1))
            db.session.add(commentLike)
        db.session.commit()