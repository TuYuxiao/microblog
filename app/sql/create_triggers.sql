use microblog;

delimiter $

#INSERT TRIGGER

create trigger category_insert before insert on Category
for each row 
begin  
  IF (new.CategoryID=new.FatherCategoryID) THEN 
    SIGNAL SQLSTATE 'HY000' SET MESSAGE_TEXT = 'Can\'t be parent of itself';
  END IF; 
end$

create trigger comment_insert before insert on Comment
for each row 
begin  
  IF (new.CommentID=new.FatherCommentID) THEN 
    SIGNAL SQLSTATE 'HY000' SET MESSAGE_TEXT = 'Can\'t be parent of itself';
  END IF;
  IF (new.FatherCommentID IS NOT NULL) THEN
    IF (new.BlogID IS NULL) THEN
      SET new.BlogID = (SELECT BlogID FROM Comment WHERE CommentID = new.FatherCommentID);
    ELSE
      IF (new.BlogID != (SELECT BlogID FROM Comment WHERE CommentID = new.FatherCommentID)) THEN
        SIGNAL SQLSTATE 'HY000' SET MESSAGE_TEXT = 'Child comment should have same BlogID';
      END IF;
    END IF;
  END IF;
end$

create trigger follow_insert before insert on Follow
for each row 
begin  
  IF (new.FollowerID=new.BeFollowedID) THEN 
    SIGNAL SQLSTATE 'HY000' SET MESSAGE_TEXT = 'Can\'t follow yourself';
  END IF; 
end$

create trigger user_insert before insert on User
for each row 
begin  
  IF (new.UserRole=0 and new.UserID != 1) THEN 
    SIGNAL SQLSTATE 'HY000' SET MESSAGE_TEXT = 'Only one ADMIN';
  END IF; 
end$



#UPDATE TRIGGER

create trigger user_update before UPDATE on User
for each row 
begin  
  IF (new.UserRole = 0 AND new.UserID != 1) THEN
    SIGNAL SQLSTATE 'HY000' SET MESSAGE_TEXT = 'Only one ADMIN tuyuxiao';
  END IF;
end$



#DELETE TRIGGER

create trigger comment_delete before delete on Comment
for each row 
begin
  DELETE FROM CommentLike WHERE CommentID = old.CommentID;
end$

create trigger blog_delete before delete on Blog
for each row 
begin
  DELETE FROM Collection WHERE BlogID = old.BlogID;
  DELETE FROM BlogLike WHERE BlogID = old.BlogID;
  DELETE FROM BlogLabel WHERE BlogID = old.BlogID;
  DELETE FROM BlogCategory WHERE BlogID = old.BlogID; 	
  SET FOREIGN_KEY_CHECKS=0;
  DELETE FROM Comment WHERE BlogID = old.BlogID;
  SET FOREIGN_KEY_CHECKS=1;
end$

create trigger category_delete before delete on Category
for each row 
begin  
  DELETE FROM BlogCategory WHERE CategoryID = old.CategoryID;
end$

create trigger user_delete before delete on User
for each row 
begin  
  IF (old.UserID = 1) THEN
    SIGNAL SQLSTATE 'HY000' SET MESSAGE_TEXT = 'Can\'t delete ADMIN';
  END IF;
  DELETE FROM Comment WHERE CommenterID = old.UserID;
  DELETE FROM Blog WHERE PublisherID = old.UserID;
  DELETE FROM Follow WHERE (FollowerID = old.UserID OR BeFollowedID = old.UserID);
end$

delimiter ;
