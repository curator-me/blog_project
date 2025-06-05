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

    # Foreign Key
    author_id = Column(Integer, ForeignKey("users.id"))

    # Relationship to User
    author = relationship("User", back_populates="blogs")

    # Relationship to Like
    likes = relationship("Like", back_populates="blog")

    # Relationship to Comment
    comments = relationship("Comment", back_populates="blog")


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

    commenter_id = Column(Integer, ForeignKey("users.id"))
    commenter = relationship("User", back_populates="comments")

    blog_id = Column(Integer, ForeignKey("blogs.id"))
    blog = relationship("Blog", back_populates="comments")
