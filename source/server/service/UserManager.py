from server.models.user import *
from server.database.setup import engine
from server.schema.structure import *
from sqlmodel import select, Session
from server.utils.exceptions import UserExists, UserDoesNotExist
from server.utils.watch_util import *
from server.utils.encription import *

"""
User Manganer Service unit

1. Creating new users
    Basic utilities with user account
2. Grabing new user
3. Making changes to user unit

-- Blind Exception Problem
Need to refactor with proper exception handling and logging
"""


class UserManager:
    """
    Abstract Class working with base database model
    """

    def __init__(self, username: str = ""):
        if username == "":
            self.existance = False
        self.username = username
        self.existance = False

        self.extract()  # Sync with Db for extraction of user information

    def extract(self):
        """
        Takes out if this name exists in DB
        falls with UserDoesNotExist Error
        """
        statement = select(User).where(User.username == self.username)
        with Session(engine) as session:
            try:
                user_object = session.exec(statement).first()
                if user_object is None:
                    raise UserDoesNotExist

                self.user_object = user_object
                self.existance = True

            except UserDoesNotExist:
                self.existance = (
                    False  # Dont touch this untill you are sure to refactor
                )
            except Exception as e:
                log.info(f"Exception Raised as {e} at User Exttraction")

    def verify_credentials(self, credentials: str):
        """
        credentials : password text
        verification with verify_password from bcripting library

        way to use with login interface - just initiate with username -> extract -> verify
        verification utility dependency
        """
        if self.existance == False:
            return None  #  User does not exist
        stored_hash = self.user_object.password
        verification = verify_password(credentials, stored_hash)
        if verification:
            return True
        else:
            return False

    def create(self, information: Input, role="student"):
        """
        Creating new user with Base Model
        Initiating its object into class object handle

        storing password
        and changing existence status
        """
        username = information.username
        password = information.password

        strong = hash_password(password)  # Hashed password
        new_user = User(username=username, password=strong, role=role)
        with Session(engine) as session:
            try:
                statement = select(User).where(User.username == username)
                result = session.exec(statement).first()
                if result is not None:
                    log.warning(f"User Exist with username : {username}")
                    raise UserExists
                log.info(f"User Creation Initiated with username : {username}")
                session.add(new_user)
                session.commit()

                statement = select(User).where(User.username == username)
                created_user = session.exec(statement).first()
                id = created_user.id  # user Id fetch

                self.existence = True
                self.user_object = created_user  # user created object
                self.username = (
                    self.user_object.username
                )  # Email update for extraction sync
            except UserExists:
                raise UserExists

            except Exception as e:
                session.rollback()
                raise Exception(f"Raised a problem with user creation : {e}")

    def distroy(self):
        statement = select(User).where(User.username == self.username)
        with Session(engine) as session:
            try:
                unit = session.exec(statement).first()  # Due to iterator object
                if unit is None:
                    self.existence = False
                    raise UserDoesNotExist
                session.delete(unit)
                session.commit()
                log.info(f"User deleted with username : {self.username}")
            except Exception as e:
                raise Exception(f"Deletion Failed with exception : {e}")
