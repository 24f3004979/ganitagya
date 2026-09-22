from server.models.user import *
from server.database import *
from sqlmodel import select

# Warning : with simple module import with wild card may lead to non-required code clash - Needs to be cleaned to insure this wont create problem

def admin_creation():
    admin = User(
        email="studjng",
        password="1234",
        role=UserRole.ADMIN
    )
    # Making transaction to data base through made object
    for _ in get_session():
        session = _
    session.add(admin)
    session.commit()
    print('User Created')

# End point testing code
def get_user():
    statement = select(User)
    for session in get_session():
        result = session.exec(statement)
        users = result.all()  # All users listing
        for _ in users:
            print(f"User : {_}")
        


# Registration core service function
def register_user(information:dict):
    '''
    Registration Service
    1. check for existing user | revert
    2. hash password
    3. Add to Db | return status code 0, 1:failed

    -- Make simple me end point for detecting user information at front end servers
    '''
    pass

