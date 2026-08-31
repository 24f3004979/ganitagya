'''
MAIN FILE
Central script for building the application up
'''
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.dev_log import log

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

# Root routing
@app.get("/")
def root():
    return "Hello Fast API setup"

@app.get("/api/v1/ping")
def pong():
    log.info("Server ping hit")
    return {"message":"pong fast api server"}

def main():
    import uvicorn
    uvicorn.run("server.main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()
