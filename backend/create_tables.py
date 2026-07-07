from database import Base, engine
import models

#Base.metadata it collect all the definition of the class that inherit from base
#create_all(engine) it create the tables
Base.metadata.create_all(engine)