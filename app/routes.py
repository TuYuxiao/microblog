#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr  5 22:15:56 2019

@author: tuyuxiao
"""

import datetime,os,shutil
from app import app,db,lm
from flask import render_template, flash, redirect, url_for, request, send_from_directory
from flask.ext.login import login_user, logout_user, current_user, login_required
from werkzeug import secure_filename
from app.models import User,Follow,Category,Blog,Comment,BlogLabel,BlogCategory,BlogLike,CommentLike
from .forms import LoginForm,SignUpForm,AboutMeForm,PublishBlogForm,UploadForm,NameForm,CommentForm,AgeForm
PER_PAGE=3

LOCAL_DIR = os.getcwd()

@lm.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route('/')
@app.route('/index')
def index():
    if current_user.is_authenticated:
        blogs = User.query.execute("SELECT * FROM Blog WHERE PublisherID in "+
                                   "(SELECT BeFollowedID FROM Follow WHERE FollowerID ="+str(current_user.UserID)
                                   +") ORDER BY PublishDate DESC LIMIT 10")
        blogs = [Blog(*blog) for blog in blogs]
        infos = []
        for blog in blogs:
            auther = User.query.execute("SELECT UserName FROM User WHERE UserID="+str(blog.PublisherID))[0][0]
            comments = Comment.query.filter_by(BlogID=blog.BlogID,count=True)
            likes = BlogLike.query.filter_by(BlogID=blog.BlogID,count=True)
            infos.append((blog,auther,comments,likes))
        return render_template('index.html',title='Home',infos=infos)
    
    return render_template('index.html',title='Home')
@app.route('/login', methods = ['GET', 'POST'])
def login():
    # 验证用户是否被验证
    if current_user.is_authenticated:
        return redirect('index')
    # 注册验证
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(UserEmail = request.form.get('email'))
        if len(user) != 0:
            user = user[0]
            if not user.check_passwd(request.form.get('password')):
                flash("Wrong password!")
                return redirect('/login')
            login_user(user)
            user.LastLoginTime = datetime.datetime.now()

            flash('Your email: ' + request.form.get('email'))
            flash('remember me? ' + str(request.form.get('remember_me')))
            return redirect(url_for("users", user_id=current_user.UserID))
        else:
            flash('Login failed, Your email is not exist!')
            return redirect('/login')

    return render_template(
        "login.html",
        title="Sign In",
        form=form)
    
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    form = SignUpForm()
    if form.validate_on_submit():
        user_name = request.form.get('user_name')
        user_email = request.form.get('user_email')
        user_password = request.form.get('password')
        register_check = User.query.filter_by(UserEmail=user_email)
        if len(register_check) != 0:
            flash("error: The email already exists!")
            return redirect('/sign-up')

        if len(user_name) and len(user_email):
            user = User(UserName=user_name,UserEmail=user_email,
                        UserPasswd=User.md5(user_password),LastLoginTime = datetime.datetime.now())
            
            db.session.add(user)
            db.session.commit()
            user = User.query.filter_by(UserEmail = user.UserEmail)
            if(len(user) == 0):
                flash("The Database error!")
                return redirect('/sign-up')

            user = user[0]
            flash("Sign up successful!")
            login_user(user)
            return redirect(url_for('users',user_id=user.UserID))

    return render_template(
        "sign_up.html",
        form=form)

@app.route('/user/<int:user_id>', defaults={'page':1}, methods=["POST", "GET"])
@app.route('/user/<int:user_id>/page/<int:page>', methods=['GET', 'POST'])
@login_required
def users(user_id,page):
    form = AboutMeForm()
    age = AgeForm()
    user = User.query.get(user_id)
    if not user:
        flash("The user is not exist.")
        redirect("/index")
    is_follow=False
    if user.UserID != current_user.UserID:
        is_follow = len(Follow.query.filter_by(FollowerID=current_user.UserID,BeFollowedID=user_id)) > 0

    pagination = Blog.query.order_by('PublishDate',desc=True).paginate(page, PER_PAGE, PublisherID = user.UserID)
    items = []
    for blog in pagination.items:
        comments = Comment.query.filter_by(BlogID=blog.BlogID,count=True)
        likes = BlogLike.query.filter_by(BlogID=blog.BlogID,count=True)
        items.append((blog,comments,likes))
    pagination.items = items
    
    follows = Follow.query.filter_by(FollowerID=user.UserID,count=True)
    fans = Follow.query.filter_by(BeFollowedID=user.UserID,count=True)

    return render_template(
        "user.html",
        form=form,
        age=age,
        user=user,
        pagination=pagination,follows=follows,fans=fans,is_follow=is_follow)
 
@app.route('/user/fan/<int:user_id>', methods=["POST", "GET"])
@login_required
def user_fans(user_id):
    followers = Follow.query.filter_by(BeFollowedID=user_id)
    current_user_followed = Follow.query.filter_by(FollowerID=current_user.UserID)
    current_user_followed = [follow.BeFollowedID for follow in current_user_followed]
    blogs = []
    fans = []
    for fan in followers:
        user = User.query.get(fan.FollowerID)
        fans.append((user,Follow.query.filter_by(FollowerID=user.UserID,count=True),
                     Follow.query.filter_by(BeFollowedID=user.UserID,count=True),user.UserID in current_user_followed))
        blogs.append(Blog.query.filter_by(PublisherID=user.UserID,count=True))
    return render_template(
        "users.html",
        users=fans,
        blogs=len(blogs))
    
@app.route('/user/follow/<int:user_id>', methods=["POST", "GET"])
@login_required
def user_follows(user_id):
    followed = Follow.query.filter_by(FollowerID=user_id)
    current_user_followed = Follow.query.filter_by(FollowerID=current_user.UserID)
    current_user_followed = [follow.BeFollowedID for follow in current_user_followed]
    blogs = []
    follows = []
    for follow in followed:
        user = User.query.get(follow.BeFollowedID)
        follows.append((user,Follow.query.filter_by(FollowerID=user.UserID,count=True),
                        Follow.query.filter_by(BeFollowedID=user.UserID,count=True),user.UserID in current_user_followed))
        blogs.append(Blog.query.filter_by(PublisherID=user.UserID,count=True))
    return render_template(
        "users.html",
        users=follows,
        blogs=len(blogs))
    
@app.route('/user/subscribe/<int:user_id>', methods=["POST", "GET"])
@login_required
def subscribe(user_id):
    follow = Follow(FollowerID=current_user.UserID,BeFollowedID=user_id)
    db.session.add(follow)
    db.session.commit()
    return ""
    
@app.route('/user/unsubscribe/<int:user_id>', methods=["POST", "GET"])
@login_required
def unsubscribe(user_id):
    follow = Follow(FollowerID=current_user.UserID,BeFollowedID=user_id)
    db.session.delete(follow)
    db.session.commit()
    return ""

@app.route('/publish', defaults={'blog_id':0}, methods=["POST", "GET"])
@app.route('/publish/<int:blog_id>', methods=["POST", "GET"])
@login_required
def publish(blog_id):
    form = PublishBlogForm(request.form)
    if blog_id == 0:
        if form.validate_on_submit():
            blog_title = request.form.get("title")
            blog_content = request.form.get("content")
            category = request.form.getlist("category")
            label = request.form.get("label")
            if not len(blog_content.strip()):
                flash("The content is necessray!")
                return redirect(url_for("publish"))
            if not len(blog_title.strip()):
                flash("The title is necessray!")
                return redirect(url_for("publish"))
            blog = Blog(BlogTitle=blog_title,BlogContent=blog_content,PublisherID=current_user.UserID)
            if db.session.add(blog):
                db.session.commit()
                blog = Blog.query.filter_by(BlogTitle=blog_title,PublisherID=current_user.UserID)[0]
                for c in category:
                    blog_category = BlogCategory(BlogID=blog.BlogID,CategoryID=int(c))
                    db.session.add(blog_category)
                db.session.commit()
                for l in label.split(';'):
                    if l.strip() != "":
                        blog_label = BlogLabel(BlogID=blog.BlogID,LabelName=l.strip())
                        db.session.add(blog_label)
                db.session.commit()
            
            else:
                flash("Database error!")
                return redirect(url_for("publish"))

            flash("Publish Successful!")
            return redirect(url_for("users", user_id=current_user.UserID,page=0))
        categories = Category.query.all()
        return render_template(
                "publish.html",
                form=form,
                categories=[(category.CategoryID,category.CategoryName) for category in categories])
    else:
        blog = Blog.query.get(blog_id)
        if form.validate_on_submit():
            blog_title = request.form.get("title")
            blog_content = request.form.get("content")
            category = request.form.getlist("category")
            label = request.form.get("label")
            if not len(blog_content.strip()):
                flash("The content is necessray!")
                return redirect(url_for("publish",blog_id=blog_id))
            if not len(blog_title.strip()):
                flash("The title is necessray!")
                return redirect(url_for("publish",blog_id=blog_id))
            if blog.BlogTitle != blog_title:
                blog.BlogTitle = blog_title
            if blog.BlogContent != blog_content:
                blog.BlogContent = blog_content
            blog.LastEditTime = datetime.datetime.now()
            BlogLabel.query.execute("DELETE FROM BlogLabel WHERE BlogID="+str(blog_id))
            BlogCategory.query.execute("DELETE FROM BlogCategory WHERE BlogID="+str(blog_id))
            db.session.commit()
            for c in category:
                blog_category = BlogCategory(BlogID=blog.BlogID,CategoryID=int(c))
                db.session.add(blog_category)
            db.session.commit()
            for l in label.split(';'):
                if l.strip() != "":
                    blog_label = BlogLabel(BlogID=blog.BlogID,LabelName=l.strip())
                    db.session.add(blog_label)
            db.session.commit()
            
            flash("Edit Successful!")
            return redirect(url_for("users", user_id=current_user.UserID,page=0))
        if not blog:
            return redirect("/index")
        if blog.PublisherID != current_user.UserID:
            flash("you can only edit your blog")
            return redirect("/index")
        labels = BlogLabel.query.filter_by(BlogID=blog.BlogID)
        if len(labels)>0:
            label = labels[0].LabelName
            for l in labels[1:]:
                label += ";"+l.LabelName
        else:
            label = ""
        category = [c.CategoryID for c in BlogCategory.query.filter_by(BlogID=blog.BlogID)]
        categories = Category.query.all()
        return render_template(
                "publish.html",
                form=form,
                blog=blog,
                label=label,
                category=category,
                categories=[(category.CategoryID,category.CategoryName) for category in categories])
            

@app.route('/user/about-me/<int:user_id>', methods=["POST", "GET"])
@login_required
def about_me(user_id):
    if user_id != current_user.UserID:
        flash("Sorry, you can only publish your description!", "error")
        return redirect("/index")
    user = User.query.get(user_id)
    if request.method == "POST":
        content = request.form.get("describe")
        if len(content) and len(content) <= 200:
            try:
                user.UserSelfDescription = content
                db.session.commit()
            except:
                flash("Database error!")
                return redirect(url_for("users", user_id=user_id))
        else:
            flash("Sorry, May be your data have some error.")
    return redirect(url_for("users", user_id=user_id))

@app.route('/user/age/<int:user_id>', methods=["POST", "GET"])
@login_required
def age(user_id):
    if user_id != current_user.UserID:
        flash("Sorry, you can only edit your age!", "error")
        return redirect("/index")
    user = User.query.get(user_id)
    if request.method == "POST":
        age = request.form.get("age")
        try:
            age = int(age)
            if  0 <= age <= 100:
                user.UserAge = age
                db.session.commit()
            else:
                flash('invalid age')
        except:
            flash('invalid age')
    return redirect(url_for("users", user_id=user_id))

@app.route('/manage', methods=["POST", "GET"])
@login_required
def manage():
    if current_user.UserRole != 0:
        flash("Sorry, you can no permission!", "error")
        return redirect("/index")
    return render_template(
        "manage.html")

def buildCommentTree(comments):
    class Node:
        def __init__(self,comment):
            self.comment = comment
            self.children = []
            self.name = ""
            self.father_name = ""
            self.is_like = False
            self.num_likes = 0
            if comment:
                self.name = User.query.execute("SELECT UserName FROM User WHERE UserID="+str(comment.CommenterID))[0][0]
                self.is_like = len(CommentLike.query.filter_by(UserID=current_user.UserID,CommentID=comment.CommentID))>0
                self.num_likes = CommentLike.query.filter_by(CommentID=comment.CommentID,count=True)
    
    root = Node(None)
    d = {}
    for comment in comments:
        node = Node(comment)
        d[str(comment.CommentID)] = node
        if not comment.FatherCommentID:
            root.children.append(node)
        else:
            if d.get(str(comment.FatherCommentID)):
                d[str(comment.FatherCommentID)].children.append(node)
                node.father_name = d[str(comment.FatherCommentID)].name
    for node in root.children:
        children = node.children.copy()
        while len(children)>0:
            child = children.pop()
            children.extend(child.children)
            node.children.extend(child.children)
    return root

def delete_comment_tree(comment_id):
    res = Comment.query.execute("SELECT CommentID FROM Comment WHERE FatherCommentID ="+str(comment_id))
    if res != ():
        for c in res:
            delete_comment_tree(c[0])
    Comment.query.execute("DELETE FROM Comment WHERE CommentID ="+str(comment_id))

@app.route('/blog/like/<int:blog_id>', methods=["POST", "GET"])
@login_required
def like_blog(blog_id):
    blogLike = BlogLike(UserID=current_user.UserID,BlogID=blog_id)
    if db.session.add(blogLike):
        db.session.commit()
        return "success"
    else:
        return "fail"
    
@app.route('/blog/unlike/<int:blog_id>', methods=["POST", "GET"])
@login_required
def unlike_blog(blog_id):
    if len(BlogLike.query.filter_by(UserID=current_user.UserID,BlogID=blog_id)) == 0:
        return "fail"
    blogLike = BlogLike(UserID=current_user.UserID,BlogID=blog_id)
    if db.session.delete(blogLike):
        db.session.commit()
        return "success"
    else:
        return "fail"

@app.route('/comment/like/<int:comment_id>', methods=["POST", "GET"])
@login_required
def like_comment(comment_id):
    commentLike = CommentLike(UserID=current_user.UserID,CommentID=comment_id)
    if db.session.add(commentLike):
        db.session.commit()
        return "success"
    else:
        return "fail"
    
@app.route('/comment/unlike/<int:comment_id>', methods=["POST", "GET"])
@login_required
def unlike_comment(comment_id):
    if len(CommentLike.query.filter_by(UserID=current_user.UserID,CommentID=comment_id)) == 0:
        return "fail"
    commentLike = CommentLike(UserID=current_user.UserID,CommentID=comment_id)
    if db.session.delete(commentLike):
        db.session.commit()
        return "success"
    else:
        return "fail"

@app.route('/blog/<int:blog_id>', methods=["POST", "GET"])
@login_required
def blog(blog_id):
    blog = Blog.query.get(blog_id)
    if not blog:
        return redirect("/index")
    if(current_user.UserID != blog.PublisherID):
        blog.PageViews = blog.PageViews + 1
    auther =User.query.execute("SELECT UserName FROM User WHERE UserID="+str(blog.PublisherID))[0][0]
    is_like_blog = len(BlogLike.query.filter_by(UserID=current_user.UserID,BlogID=blog_id))>0
    num_likes = BlogLike.query.filter_by(BlogID=blog_id,count=True)
    comments = Comment.query.filter_by(BlogID=blog_id)
    root = buildCommentTree(comments)
    comment = CommentForm()
    return render_template(
        "blog.html",
        blog=blog,
        root=root,
        comment_form=comment,
        num_likes=num_likes,
        is_like_blog=is_like_blog,
        auther=auther)
    
@app.route('/blog/delete/<int:blog_id>/<int:page>', methods=["POST", "GET"])
@login_required
def delete_blog(blog_id, page):
    blog = Blog.query.get(blog_id)
    if not blog:
        return redirect("/index")
    if blog.PublisherID != current_user.UserID:
        flash("Sorry, you can only delete your blog!", "error")
        return redirect("/index")
    db.session.delete(blog)
    db.session.commit()
    return redirect(url_for('users',user_id=current_user.UserID, page=page))

@app.route('/comment/<int:user_id>/<int:blog_id>', methods=["POST", "GET"])
@login_required
def comment(user_id,blog_id):
    if user_id != current_user.UserID:
        flash("Sorry, you can only comment as others", "error")
        return redirect("/index")
    father_comm_id = int(request.form.get("replyid"))
    if father_comm_id == 0:
        comm = Comment(CommentContent=request.form.get("content"),BlogID=blog_id,CommenterID=user_id)
    else:
        comm = Comment(CommentContent=request.form.get("content"),BlogID=blog_id,CommenterID=user_id,
                       FatherCommentID=father_comm_id)

    db.session.add(comm)
    db.session.commit()
    return redirect(url_for('blog',blog_id=blog_id))

@app.route('/comment/delete/<int:comment_id>', methods=["POST", "GET"])
@login_required
def delete_comment(comment_id):   
    comm = Comment.query.get(comment_id)
    if not comm:
        return redirect("/index")
    if comm.CommenterID != current_user.UserID:
        flash("Sorry, you can only delete your comment!", "error")
        return redirect("/index")
    
    delete_comment_tree(comment_id)
    db.session.commit()
    return redirect(url_for('blog',blog_id=comm.BlogID))

@app.route('/category', methods=["POST", "GET"])
@login_required
def category():
    if current_user.UserRole != 0:
        flash("Sorry, you can no permission!", "error")
        return redirect("/index")
    categories = Category.query.all()
    id_name_dict = {}
    for c in categories:
        id_name_dict[str(c.CategoryID)] = c.CategoryName
    return render_template(
            "category_manage.html",
            categories=categories,
            id_name_dict = id_name_dict)

@app.route('/blog/manage/<int:page>', methods=["POST", "GET"])
@login_required
def blog_manage(page):
    if current_user.UserRole != 0:
        flash("Sorry, you can no permission!", "error")
        return redirect("/index")
    pagination = Blog.query.order_by('PublishDate',desc=True).paginate(page, PER_PAGE)
    items = []
    for blog in pagination.items:
        auther = User.query.execute("SELECT UserName FROM User WHERE UserID="+str(blog.PublisherID))[0][0]
        comments = Comment.query.filter_by(BlogID=blog.BlogID,count=True)
        likes = BlogLike.query.filter_by(BlogID=blog.BlogID,count=True)
        items.append((blog,auther,comments,likes))
    pagination.items = items
    return render_template(
            "blog_manage.html",
            pagination=pagination)

@app.route('/blog/manage/delete/<int:blog_id>/<int:page>', methods=["POST", "GET"])
@login_required
def blog_manage_delete(blog_id, page):
    if current_user.UserRole != 0:
        flash("Sorry, you can no permission!", "error")
        return redirect("/index")
    blog = Blog.query.get(blog_id)
    if not blog:
        flash('database error!')
        return redirect(url_for('blog_manage', page=page))
    db.session.delete(blog)
    db.session.commit()
    return redirect(url_for('blog_manage', page=page))

def getChildCategory(categories,cid):
    d = {}
    for category in categories:
        d[str(category.CategoryID)] = []
    for category in categories:
        if category.FatherCategoryID is not None:
            d[str(category.FatherCategoryID)].append(str(category.CategoryID))
    temp = []
    res = [cid]
    temp.extend(d[str(cid)])
    while len(temp)>0:
        category = temp.pop()
        if not int(category) in res:
            res.append(int(category))
            temp.extend(d[category])
    return res

@app.route('/category/edit/<int:category_id>', methods=["POST", "GET"])
@login_required
def edit_category(category_id):
    if current_user.UserRole != 0:
        flash("Sorry, you can no permission!", "error")
        return redirect("/index")
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        father = int(request.form.getlist("father")[0])
        if father == 0:
            father = None
        if category_id == 0:
            category = Category(CategoryName=name,CategoryDescription=description,FatherCategoryID=father)
            db.session.add(category)
        else:
            categories = Category.query.all()
            cids = getChildCategory(categories,category_id)
            if father in cids:
                flash("a category can't be the father of its children")
                return redirect("/category")
            category = Category.query.get(category_id)
            if category.CategoryName != name:
                category.CategoryName = name
            if category.CategoryDescription != description:
                category.CategoryDescription = description
            if category.FatherCategoryID != father:
                category.FatherCategoryID = father
        db.session.commit()
        return redirect("/category")
    categories = Category.query.all()
    filtered_categories = []
    if category_id == 0:
        category = Category(CategoryID=0,CategoryName="",CategoryDescription="",FatherCategoryID=0)
    else:
        category = Category.query.get(category_id)
        cids = getChildCategory(categories,category_id)
        for c in categories:
            if not c.CategoryID in cids:
                filtered_categories.append(c)
    categories = [(c.CategoryID,c.CategoryName) for c in filtered_categories]
    return render_template(
            "category.html",
            category=category,
            categories=categories)
    
@app.route('/category/delete/<int:category_id>', methods=["POST", "GET"])
@login_required
def delete_category(category_id):
    if current_user.UserRole != 0:
        flash("Sorry, you can no permission!", "error")
        return redirect("/index")
    category = Category.query.get(category_id)
    Category.query.execute("UPDATE Category SET FatherCategoryID = null WHERE FatherCategoryID="+str(category_id))
    db.session.delete(category)
    db.session.commit()
    return redirect('/category')