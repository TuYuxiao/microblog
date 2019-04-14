#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr  6 23:49:33 2019

@author: tuyuxiao
"""

from app.models import User,Follow,Category,Blog,Comment,BlogLabel,BlogCategory,BlogLike,CommentLike

def generateData(numUser,numCategory,numBlog):
    User.fake(numUser)
    
    Follow.fake(numUser)
        
    Category.fake(numCategory)
    
    Blog.fake(numBlog,numUser)
    
    Comment.fake(numBlog,numUser)
    
    BlogCategory.fake(numBlog,numCategory*5)
    
    BlogLabel.fake(numBlog)
    
    BlogLike.fake(numBlog*3,numUser,numBlog)
    
    CommentLike.fake(numBlog*10,numUser,numBlog*8)