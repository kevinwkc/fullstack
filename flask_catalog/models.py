
#from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, ForeignKey, Integer, String, Date, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))
    item = relationship("Item", back_populates="user")
'''

    
    username = Column(String(64), primary_key=True)
    password_hash = Column(String(128))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
'''

                   
    
class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True)    
    item = relationship("Item", back_populates="category")
    
    def __repr__(self):
        return '<Category %r>' % self.name
    
    @property 
    def serialize(self):
        return { "id": self.id, 
                "name": self.name
                ,'item': [i.serialize for i in self.item]
                }

                 
class Item(Base):
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey('category.id')) #using __tablename__    
    category = relationship("Category", back_populates="item") #, backref="item")
    name = Column(String(64), index=True, unique=True)
    description =Column(String(64), nullable=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship("User", back_populates="item")
    '''
        shelter_id = Column(Integer, ForeignKey('shelter.id'))
        shelter = relationship(Shelter) #relationship class for Foreign Key
    '''    
    
    def __repr__(self):
        return '<Item %r>' % self.name
    
    @property
    def serialize(self):
        return {"id": self.id, 
                "user_id": self.user_id,
                "category_id": self.category_id,
                "name": self.name,
                "description": self.description }

engine = create_engine('sqlite:///catalog.db')
#Base.metadata.bind = engine
Base.metadata.create_all(engine)
