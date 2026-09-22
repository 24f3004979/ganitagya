'''
MAIN FILE
Central script for building the application up
'''
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# custom units import
from server.dev_log import log
from server.database import *
from server.service.user import admin_creation, get_user

app = FastAPI(title='server')

# cross origin request
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

log.info('Fast Api app created')
Initiate_database() # Initiates all required models
log.info("Data Base started")

admin_creation()
print(f"Admin Created")

# Dummy function for testing data base setup test fetch
get_user()

# Root routing
@app.get("/")
def root():
    return "Hello Fast API setup"


# Server Made with Uvicorn
def main():
    import uvicorn
    uvicorn.run("server.main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()
