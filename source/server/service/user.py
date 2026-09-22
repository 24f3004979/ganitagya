from server.models.user import *
from server.src.service.database import *

# Module bounding errors with loading services - Need to sort out with directory structure refactor at server end

def admin_creation():
    new = User(
        email="Admin",
        password="1234",
        role=UserRole.ADMIN
    )

    print(f"User Created")

admin_creation()
