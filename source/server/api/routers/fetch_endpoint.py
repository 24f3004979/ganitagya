'''
Information fetching endpoints

Endpoints for fetching information about user and their roles
'''
from fastapi import APIRouter, status, HTTPException, Depends

# Required imports for fetch endpoints
from server.utils.authorization_utils import get_role, get_id
from server.utils.watch_util import log


fetch_router = APIRouter()


@fetch_router.get("/id")
def fetch_id(user_name: str):
    return get_id(user_name)


@fetch_router.get("/role")
def fetch_role(username: str):
    """Fetch current user role for authorization for certain routs"""
    return get_role(username)  # role fetch
