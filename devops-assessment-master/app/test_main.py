"""Tests for the FastAPI service."""
import os

os.environ.setdefault("CONFIG_DB_PATH", "test_config.db")

from fastapi.testclient import TestClient

import main

client = TestClient(main.app)


def setup_function() -> None:
    """Reset the persisted store before each test."""
    main.init_db()
    with main._connect() as conn:
        conn.execute("DELETE FROM config")


def test_health() -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_version() -> None:
    resp = client.get("/version")
    assert resp.status_code == 200
    assert resp.json() == {"version": main.VERSION}


def test_env(monkeypatch) -> None:
    monkeypatch.setenv("ENVIRONMENT", "test")
    # Reload module so the ENVIRONMENT value is re-read at request time.
    resp = client.get("/env")
    assert resp.status_code == 200
    assert resp.json() == {"environment": "test"}


def test_config_crud() -> None:
    payload = {"name": "database_url", "value": "postgres://example"}

    # Create
    resp = client.post("/config", json=payload)
    assert resp.status_code == 201
    assert resp.json() == payload

    # Read
    resp = client.get("/config/database_url")
    assert resp.status_code == 200
    assert resp.json() == payload

    # Delete
    resp = client.delete("/config/database_url")
    assert resp.status_code == 200
    assert resp.json() == {"deleted": True}

    # Read after delete -> 404
    resp = client.get("/config/database_url")
    assert resp.status_code == 404


def test_config_not_found() -> None:
    assert client.get("/config/missing").status_code == 404
    assert client.delete("/config/missing").status_code == 404


