'''
MAIN FILE
Central script for building the application up
'''
from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
# security import for token generation
import jwt
from fastapi.security import OAuth2PasswordRequestForm


# custom units import
from server.database import *
from server.service.user import admin_creation, get_users
from server.api.v1.routes import router as v1_router


app = FastAPI(title='server')

# cross origin request
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SQLModel.metadata.drop_all(engine)  # reset data base
Initiate_database() # Initiates all required models

admin_creation()
print(f"Admin Created")

app.include_router(v1_router, prefix="/api/v1")

# Root routing
@app.get("/")
def root():
    return "Hello fast api"

# Server Made with Uvicorn
def main():
    import uvicorn
    uvicorn.run("server.main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()
