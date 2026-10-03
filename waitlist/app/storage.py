"""Two interchangeable backends. Both expose add(username) -> True if newly added."""
import hashlib
import sqlite3
from contextlib import closing
from datetime import datetime, timezone


class SqliteStorage:
    """Local development only. Cloud Run's disk is wiped between restarts."""

    def __init__(self, path: str):
        self._path = path
        with closing(sqlite3.connect(self._path)) as c:
            c.execute(
                "CREATE TABLE IF NOT EXISTS waitlist ("
                "username TEXT PRIMARY KEY, created_at TEXT NOT NULL)"
            )
            c.commit()

    def add(self, username: str) -> bool:
        now = datetime.now(timezone.utc).isoformat()
        with closing(sqlite3.connect(self._path)) as c:
            cur = c.execute(
                "INSERT OR IGNORE INTO waitlist (username, created_at) VALUES (?, ?)",
                (username, now),
            )
            c.commit()
            return cur.rowcount == 1


class FirestoreStorage:
    """Production. Persistent, and covered by Google Cloud's free tier at this scale."""

    def __init__(self, collection: str):
        from google.cloud import firestore

        self._server_ts = firestore.SERVER_TIMESTAMP
        self._col = firestore.Client().collection(collection)

    def add(self, username: str) -> bool:
        from google.api_core.exceptions import AlreadyExists

        # Hash of the username as document ID = built-in de-duplication
        doc_id = hashlib.sha256(username.encode()).hexdigest()
        try:
            self._col.document(doc_id).create(
                {"username": username, "created_at": self._server_ts, "source": "landing"}
            )
            return True
        except AlreadyExists:
            return False


def build_storage(settings):
    if settings.storage == "firestore":
        return FirestoreStorage(settings.firestore_collection)
    return SqliteStorage(settings.sqlite_path)
