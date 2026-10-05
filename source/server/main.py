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
from server.api.routers.student_endpoint import student_router
from server.api.routers.siddhi_endpoint import siddhi_router

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
app.include_router(student_router, prefix="/api/v1/student")
app.include_router(siddhi_router, prefix="/api/v1/siddhi")


# Root routing
@app.get("/")
def root():
    log.info("serving Root page")
    return "Hello fast api"

''' Local development server
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

'''
# Production server startup
def main():
    import os
    import uvicorn

    # Render provides the port dynamically via the PORT environment variable
    # Locally, it falls back to 8000
    port = int(os.getenv("PORT", 8000))

    # Turn off reload in production to avoid performance and environment errors
    is_production = os.getenv("RENDER") is not None
    should_reload = not is_production

    uvicorn.run(
        "server.main:app",
        host="0.0.0.0",
        port=port,
        reload=should_reload,
        reload_excludes=["db/", "app.log"],
    )
