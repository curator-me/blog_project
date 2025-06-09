from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base



class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)
    firstname = Column(String, nullable=True)
    lastname = Column(String, nullable=True)
    location = Column(String, nullable=True)
    disabled = Column(Boolean, default=False)

    blogs = relationship('Blog', back_populates='author')
    likes = relationship('Like', back_populates='liked_by')
    comments = relationship('Comment', back_populates='commenter')
 

class Blog(Base):
    __tablename__ = "blogs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    body = Column(String, nullable=False)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)

    author_id = Column(Integer, ForeignKey("users.id"))             ## "tablename.column"
    catagory_id = Column(Integer, ForeignKey("catagories.id"))

    # Relationship to User, Like, Comment
    author = relationship("User", back_populates="blogs")           ## BaseName, B_P = Relastionship model name of 
    likes = relationship("Like", back_populates="blog")             ## that BaseName model for connecting
    comments = relationship("Comment", back_populates="blog")
    catagory = relationship("Catagory", back_populates="blogs")


class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True)
    time_liked = Column(DateTime(timezone=True), server_default=func.now())
    
    reactor_id = Column(Integer, ForeignKey("users.id"))
    liked_by = relationship("User", back_populates="likes")

    blog_id = Column(Integer, ForeignKey("blogs.id"))
    blog = relationship("Blog", back_populates="likes")

class Comment(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True, index=True)
    body = Column(String, nullable=False)
    time_commented = Column(DateTime(timezone=True), server_default=func.now())
    # time_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    commenter_id = Column(Integer, ForeignKey("users.id"))
    commenter = relationship("User", back_populates="comments")

    blog_id = Column(Integer, ForeignKey("blogs.id"))
    blog = relationship("Blog", back_populates="comments")

class Catagory(Base):
    __tablename__ = 'catagories'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    blogs = relationship("Blog", back_populates="catagory")


class Tags(Base):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True, index=True)

