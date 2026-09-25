from server.models.user import *
from server.database import engine
from sqlmodel import select, Session 
from server.exceptions import UserExists
from server.dev_log import *
from server.utils.auth_utils import *

'''
User Manganer Service unit

1. Creating new users
    Basic utilities with user account
2. Grabing new user
3. Making changes to user unit
'''

class UserManager:
    '''
    Abstract Class working with base database model
    '''

    def __init__(self, email):
        self.email = email
        self.user_object = None
        self.existance = True

        self.extract() # Sync with Db for extraction of user information

    def extract(self):
        '''
        Takes out if this name exists in DB
        falls with UserDoesNotExist Error
        '''
        statement = select(User).where(User.email == self.email)
        with Session(engine) as session:
            try:
                user_object = session.exec(statement).first()
                if user_object is None:
                    raise UserDoesNotExist

                self.user_object = user_object

            except UserDoesNotExist as e:
                self.existance = False
            except Exception as e:
                log.info(f'Exception Raised as {e} at User Exttraction')

    def verify_credentials(self, credentials:str):
        '''
        credentials : password text
        verification with verify_password from bcripting library

        verification utility dependency
        '''
        if self.existance == False:
            return None #  User does not exist
        stored_hash = self.user_object.password
        verification = verify_password(credentials, stored_hash)
        if verification:
            return True
        else:
            return False

    def create(self, information:dict):
        '''
        Creating new user with Base Model
        Initiating its object into class object handle

        storing password
        and changing existence status
        '''
        email = information["email"]
        password = information["password"]

        strong = hashed_password(password) # Hashed password
        new_user = User(
                email=email, 
                password=strong
                )
        with Session(engine) as session:
            try:
                session.add(new_user)
                session.commit()

                statement = select(User).where(User.email == email)
                created_user = session.exec(statement).first()
                id = created_user.id  # user Id fetch

                self.existence = True
                self.user_object = created_user  # user created object
                self.email = user_object.email # Email update for extraction sync

            except Exception as e:
                session.rollback()
                raise Exception(f"Raised a problem with user creation : {e}")

    def distroy(self):
        statement = select(User).where(User.email == self.email)
        with Session(engine) as session:
            try:
                unit = session.exec(statement).first() # Due to iterator object
                if unit is None:
                    self.existence = False
                    raise UserDoesNotExist
                session.delete(unit)
                session.commit()
                log.info(f"User deleted with email : {self.email}")
            except Exception as e:
                riase Exception(f"Deletion Failed with exception : {e}")
