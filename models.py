from sqlalchemy import Boolean, Column, ForeignKey, Index, Integer, String, DateTime, Table, exists
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


blog_tag = Table(
    'blog_tag', 
    Base.metadata,
    Column('blog_id', ForeignKey('blogs.id', ondelete="CASCADE"), primary_key=True),
    Column('tag_id', ForeignKey('tags.id', ondelete="CASCADE"), primary_key=True),
)

favourite_blog_table = Table(
    'favourite_blog',
    Base.metadata,
    Column('user_id', ForeignKey('users.id', ondelete="CASCADE"), primary_key=True),
    Column('blog_id', ForeignKey('blogs.id', ondelete="CASCADE"), primary_key=True),
    Column('added_at', DateTime, server_default=func.now()),
    Index('idx_favorite_user', 'user_id'),
    Index('idx_favorite_blog', 'blog_id'),
)

class History(Base):
    __tablename__ = 'history'

    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), primary_key=True)
    blog_id = Column(Integer, ForeignKey('blogs.id', ondelete="CASCADE"), primary_key=True)
    viewed_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="history")
    blog = relationship("Blog", back_populates="history")



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
    favorite_blogs = relationship('Blog', secondary=favourite_blog_table, back_populates='favorited_by')

    history = relationship('History', back_populates='user')
    
 

class Blog(Base):
    __tablename__ = "blogs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    body = Column(String, nullable=False)
    # search_vector = Column(TSVectorType('title', 'content'))  # Special column for full-text search (postgresql)

    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    favourite_count = Column(Integer, default=0)
    view_count = Column(Integer, default=0)

    author_id = Column(Integer, ForeignKey("users.id"))             ## "tablename.column"
    category_id = Column(Integer, ForeignKey("catagories.id"))

    # Relationship to User, Like, Comment
    author = relationship("User", back_populates="blogs") 
    likes = relationship("Like", back_populates="blog")
    comments = relationship("Comment", back_populates="blog")
    category = relationship("Category", back_populates="blogs")

    favorited_by = relationship('User', secondary=favourite_blog_table, back_populates='favorite_blogs')
    tags = relationship("Tag", secondary=blog_tag, back_populates="blogs")

    ''' object_name = relationship(
       'model_name', 
        secondary = association_table_name, 
        back_populates = 'relationship_object_name')
    '''
    history = relationship('History', back_populates='blog')

    def is_favorited(self, user_id, blog_id, db):
        return db.query(
            exists().where(
                favourite_blog_table.c.user_id == user_id,
                favourite_blog_table.c.blog_id == blog_id,
            )
        )

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
    time_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    commenter_id = Column(Integer, ForeignKey("users.id"))
    commenter = relationship("User", back_populates="comments")

    blog_id = Column(Integer, ForeignKey("blogs.id"))
    blog = relationship("Blog", back_populates="comments")

class Category(Base):
    __tablename__ = 'catagories'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)

    blogs = relationship("Blog", back_populates="category")


class Tag(Base):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Integer, nullable=False, unique=True)

    blogs = relationship("Blog", secondary=blog_tag, back_populates='tags')

