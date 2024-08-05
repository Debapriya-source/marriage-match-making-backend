from sqlalchemy import Column, Integer, String, ARRAY
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), index=True)
    age = Column(Integer)
    gender = Column(String(15))
    email = Column(String(50), unique=True, index=True)
    city = Column(String(50), index=True)
    # interests = Column(ARRAY(String(50)))
    interests = Column(String(255))
