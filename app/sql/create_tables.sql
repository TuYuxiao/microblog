use microblog;

CREATE TABLE IF NOT EXISTS User
(
  UserID INT NOT NULL AUTO_INCREMENT,
  UserName VARCHAR(20) NOT NULL,
  UserPasswd CHAR(32) NOT NULL,
  UserEmail VARCHAR(32) NOT NULL UNIQUE,
  UserRole INT NOT NULL DEFAULT 1,
  UserSelfDescription VARCHAR(200),
  UserAge INT,
  RegistrationTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  LastLoginTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  Avator VARCHAR(5000),
  PRIMARY KEY (UserID),
  UNIQUE (UserEmail)
) character set = utf8;
INSERT INTO User(UserName,UserPasswd,UserEmail,UserRole,UserSelfDescription) VALUES('tuyuxiao','d80f4471245f4489c6b991fd6ebe1ab2','116010210@link.cuhk.edu.cn',0,'Administrator of MicroBlog');

CREATE TABLE IF NOT EXISTS Follow
(
  FollowerID INT NOT NULL,
  BeFollowedID INT NOT NULL,
  PRIMARY KEY (FollowerID, BeFollowedID),
  FOREIGN KEY (FollowerID) REFERENCES User(UserID),
  FOREIGN KEY (BeFollowedID) REFERENCES User(UserID)
) character set = utf8;

CREATE TABLE IF NOT EXISTS Category
(
  CategoryID INT NOT NULL AUTO_INCREMENT,
  CategoryName VARCHAR(20) NOT NULL UNIQUE,
  CategoryDescription VARCHAR(50),
  FatherCategoryID INT,
  PRIMARY KEY (CategoryID),
  FOREIGN KEY (FatherCategoryID) REFERENCES Category(CategoryID)
) character set = utf8;
INSERT INTO Category(CategoryName) VALUES ('Uncategorized');

CREATE TABLE IF NOT EXISTS Blog
(
  BlogID INT NOT NULL AUTO_INCREMENT,
  PublishDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  LastEditTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  BlogTitle VARCHAR(30) NOT NULL,
  BlogContent VARCHAR(5000) NOT NULL,
  PageViews INT DEFAULT 0,
  PublisherID INT NOT NULL,
  PRIMARY KEY (BlogID),
  FOREIGN KEY (PublisherID) REFERENCES User(UserID)
) character set = utf8;

CREATE TABLE IF NOT EXISTS Comment
(
  CommentID INT NOT NULL AUTO_INCREMENT,
  CommentDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CommentContent VARCHAR(300) NOT NULL,
  BlogID INT NOT NULL,
  CommenterID INT NOT NULL,
  FatherCommentID INT,
  PRIMARY KEY (CommentID),
  FOREIGN KEY (BlogID) REFERENCES Blog(BlogID),
  FOREIGN KEY (CommenterID) REFERENCES User(UserID),
  FOREIGN KEY (FatherCommentID) REFERENCES Comment(CommentID)
) character set = utf8;

CREATE TABLE IF NOT EXISTS BlogCategory
(
  BlogID INT NOT NULL,
  CategoryID INT NOT NULL,
  PRIMARY KEY (BlogID, CategoryID),
  FOREIGN KEY (BlogID) REFERENCES Blog(BlogID),
  FOREIGN KEY (CategoryID) REFERENCES Category(CategoryID)
) character set = utf8;

CREATE TABLE IF NOT EXISTS BlogLabel
(
  BlogID INT NOT NULL,
  LabelName VARCHAR(20) NOT NULL,
  PRIMARY KEY (BlogID, LabelName),
  FOREIGN KEY (BlogID) REFERENCES Blog(BlogID)
) character set = utf8;

CREATE TABLE IF NOT EXISTS BlogLike
(
  UserID INT NOT NULL,
  BlogID INT NOT NULL,
  LikeTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (UserID, BlogID),
  FOREIGN KEY (UserID) REFERENCES User(UserID),
  FOREIGN KEY (BlogID) REFERENCES Blog(BlogID)
) character set = utf8;

CREATE TABLE IF NOT EXISTS CommentLike
(
  UserID INT NOT NULL,
  CommentID INT NOT NULL,
  LikeTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (UserID, CommentID),
  FOREIGN KEY (UserID) REFERENCES User(UserID),
  FOREIGN KEY (CommentID) REFERENCES Comment(CommentID)
) character set = utf8;

CREATE TABLE IF NOT EXISTS Collection
(
  UserID INT NOT NULL,
  BlogID INT NOT NULL,
  CollectTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (UserID, BlogID),
  FOREIGN KEY (UserID) REFERENCES User(UserID),
  FOREIGN KEY (BlogID) REFERENCES Blog(BlogID)
) character set = utf8;

