from .database import Base
from sqlalchemy import Column, Integer, String, Boolean, true, ForeignKey
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship


class Post(Base):
    __tablename__ = "post"

    id = Column(Integer, primary_key = True, nullable = False)
    title = Column(String, nullable = False)
    content = Column(String, nullable = False)
    published = Column(Boolean, server_default= 'True')
    createdat = Column(TIMESTAMP(timezone=True), nullable = False, server_default=text('now()'))
    user_id = Column(Integer, ForeignKey("users.id", ondelete= "CASCADE"), nullable = False)

    user = relationship("User")

class User(Base):
    __tablename__ = "users"

    email = Column(String, nullable = False, unique=True)
    password = Column(String, nullable = False)
    id = Column(Integer, primary_key = True, nullable = False)
    createdat = Column(TIMESTAMP(timezone=True), nullable = False, server_default=text('now()'))

class Vote(Base):
    __tablename__ = "votes"

    user_id = Column(Integer, ForeignKey("users.id", ondelete= "CASCADE"), nullable = False, primary_key = True)
    post_id = Column(Integer, ForeignKey("post.id", ondelete= "CASCADE"), nullable = False, primary_key = True)

