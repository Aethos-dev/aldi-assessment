"""Simple FastAPI service for the DevOps assessment.

Exposes health, version and env endpoints plus a small key/value
configuration store persisted to SQLite on a mounted PersistentVolume.
"""
import os
import sqlite3
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

# Application version. Can be overridden at build/deploy time via env var.
VERSION = os.environ.get("APP_VERSION", "1.0.0")

# Path to the SQLite database file. In Kubernetes this points at a
# PersistentVolume mount (see helm/templates/pvc.yaml). Defaults to a
# local file for development/testing.
DB_PATH = os.environ.get("CONFIG_DB_PATH", "config.db")


def _connect() -> sqlite3.Connection:
    """Open a SQLite connection with row access by column name."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create the config table if it does not already exist."""
    with _connect() as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS config ("
            "name TEXT PRIMARY KEY, value TEXT NOT NULL)"
        )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Initialise the database schema on startup."""
    init_db()
    yield


app = FastAPI(title="DevOps Assessment Service", version=VERSION, lifespan=lifespan)


class ConfigItem(BaseModel):
    """Request/response model for a configuration entry."""

    name: str
    value: str


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness/readiness probe endpoint."""
    return {"status": "ok"}


@app.get("/version")
def version() -> dict[str, str]:
    """Return the application version."""
    return {"version": VERSION}


@app.get("/env")
def env() -> dict[str, str]:
    """Return the value of the ENVIRONMENT variable."""
    return {"environment": os.environ.get("ENVIRONMENT", "unknown")}


@app.post("/config", response_model=ConfigItem, status_code=status.HTTP_201_CREATED)
def set_config(item: ConfigItem) -> ConfigItem:
    """Create or update a configuration entry."""
    with _connect() as conn:
        conn.execute(
            "INSERT INTO config (name, value) VALUES (?, ?) "
            "ON CONFLICT(name) DO UPDATE SET value = excluded.value",
            (item.name, item.value),
        )
    return item


@app.get("/config/{name}", response_model=ConfigItem)
def get_config(name: str) -> ConfigItem:
    """Return a single configuration entry by name."""
    with _connect() as conn:
        row = conn.execute(
            "SELECT value FROM config WHERE name = ?", (name,)
        ).fetchone()
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"config '{name}' not found",
        )
    return ConfigItem(name=name, value=row["value"])


@app.delete("/config/{name}")
def delete_config(name: str) -> dict[str, bool]:
    """Delete a configuration entry by name."""
    with _connect() as conn:
        cur = conn.execute("DELETE FROM config WHERE name = ?", (name,))
        if cur.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"config '{name}' not found",
            )
    return {"deleted": True}

