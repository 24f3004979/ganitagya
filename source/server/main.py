"""
MAIN FILE

Load requirements
1. routes
2. global configs
3. DB Models
4. Middlewares [ to make ]
5. CORS enabled
"""

# External dependency
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Custom Module import
from server.database.setup import Initiate_database
from server.utils.watch_util import log

# Routers
from server.api.routers.auth_endpoint import auth_router
from server.api.routers.fetch_endpoint import fetch_router

# Global Configs
from server.config import *

app = FastAPI(title="server")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Initiate_database()

app.include_router(auth_router, prefix="/api/v1/auth")
app.include_router(fetch_router, prefix="/api/v1/fetch")


# Root routing
@app.get("/")
def root():
    log.info("serving Root page")
    return "Hello fast api"


# Server Made with Uvicorn
def main():
    import uvicorn

    uvicorn.run(
        "server.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_excludes=["db/", "app.log"],
    )


if __name__ == "__main__":
    main()
