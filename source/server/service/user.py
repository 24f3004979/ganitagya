from server.models.user import *
from server.database import *
from sqlmodel import select
import bcrypt
from server.exceptions import UserExists

# Warning : with simple module import with wild card may lead to non-required code clash - Needs to be cleaned to insure this wont create problem
    
def hash_password(plain_password: str) -> str:
    password_bytes = plain_password.encode('utf-8')
    salt = bcrypt.gensalt(rounds=12)
    hashed_bytes = bcrypt.hashpw(password_bytes, salt)
    return hashed_bytes.decode('utf-8')


def verify_password(plain_password: str, stored_hash: str) -> bool:
    password_bytes = plain_password.encode('utf-8')
    hash_bytes = stored_hash.encode('utf-8')
    
    return bcrypt.checkpw(password_bytes, hash_bytes)


def admin_creation():
    admin = User(
        email="Admina",
        password="1234",
        role="admin"
    )
    # Making transaction to data base through made object
    for _ in get_session():
        session = _
    session.add(admin)
    session.commit()
    print('User Created')

# End point testing code
def get_users():
    statement = select(User)
    for session in get_session():
        result = session.exec(statement)
        users = result.all()  # All users listing
        for _ in users:
            print(f"User : {_}")
        return users
        
# Registration core service function
def register_user(information:dict):
    '''
    input: information {
        email : str,
        password : str,
        role : str
    }
    '''
    email = information["email"]
    statement = select(User).where(User.email == email)
    for _ in get_session():
        session = _
        search = session.exec(statement).first()
        if (email == search):
            session.rollback()

            raise UserExists

        new_user = User(
                email = email,
                password = hash_password(information["password"]),
                role = information["role"]
                )
        try:
            session.add(new_user)
            session.commit()
            print("User created")
            return True
        except Exception as e:
             raise Exception(f"Exception raised during user creation : {e}")

def verify_user(information:dict):
    email = information["email"]
    statement = select(User).where(User.email == email)
    for _ in get_session():
        session = _
        user = session.exec(statement).first()
        if user:
            password = information["password"]
            hashed_password = user.password
            verification = verify_password(password, hashed_password)
            if verification:
                return True, user.role
        return False
