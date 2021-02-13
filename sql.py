import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()

class Word(Base):
    __tablename__ = 'word'
    # Here we define columns for the table person
    # Notice that each column is also a normal Python instance attribute.
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), index=True)
    part = Column(String(20), index=True)
    gender = Column(String(20), index=True)
    form = Column(Integer, index=True)

    syllables = Column(String(10), index=True)
    tail = Column(String(10), index=True)

    base_id = Column(Integer, ForeignKey('word.id', use_alter=True))
    base = relationship("Word", remote_side=[id], backref="forms")




# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.
engine = create_engine('sqlite:///sqlalchemy_example.db')

# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.create_all(engine)

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
#
# session = DBSession()
#
# person1 = Person(login="John", password='123')
# session.add(person1)
#
# resume1 = Resume(education="1234", experience="1kmdsfkjnv", person=person1)
# session.add(resume1)
#
# company1 = Company(name="company1")
# company1.resumes.append(resume1)
# session.add(company1)
# company2 = Company(name="company2")
# company2.resumes.append(resume1)
# session.add(company2)
#
# session.commit()
#
# print([c.name for c in  session.query(Company).filter(Company.resumes.any(Resume.person.has(id=person1.id))).all()])

