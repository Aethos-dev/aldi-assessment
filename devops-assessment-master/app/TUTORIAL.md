# FastAPI Tutorial (Based on This Codebase)

This tutorial teaches the core concepts of [FastAPI](https://fastapi.tiangolo.com/)
by walking through the real service in this repository: [`main.py`](./main.py).

The service is tiny but touches every fundamental you need:

- Creating an app
- GET endpoints returning JSON
- Reading configuration from environment variables
- Request/response validation with **Pydantic** models
- Path parameters
- Proper HTTP status codes and error handling
- Testing with `TestClient`
- Running it (locally and in Docker)

---

## 1. Prerequisites

- Python 3.12+
- The dependencies in [`requirements.txt`](./requirements.txt):

```text
fastapi==0.115.0
uvicorn[standard]==0.30.6
```

Install everything (including the test dependency) into a virtual environment:

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# macOS/Linux
# source .venv/bin/activate

pip install -r requirements.txt
pip install -r requirements-dev.txt   # httpx + pytest for tests
```

- `fastapi` — the web framework.
- `uvicorn[standard]` — the ASGI server that actually runs the app.

---

## 2. Creating the application

```python
import os
from fastapi import FastAPI

VERSION = os.environ.get("APP_VERSION", "1.0.0")

app = FastAPI(title="DevOps Assessment Service", version=VERSION)
```

**What's happening:**

- `FastAPI(...)` creates the application object. Everything else attaches to `app`.
- `title` and `version` show up automatically in the generated API docs.
- `VERSION` is read from the `APP_VERSION` environment variable, falling back to
  `"1.0.0"`. This is a common 12-factor pattern: configuration comes from the
  environment, not hardcoded values.

> 💡 The name `app` matters. When we run the server with
> `uvicorn main:app`, `main` is the module (`main.py`) and `app` is this object.

---

## 3. Your first endpoint: `GET /health`

```python
@app.get("/health")
def health() -> dict[str, str]:
    """Liveness/readiness probe endpoint."""
    return {"status": "ok"}
```

**Key ideas:**

- `@app.get("/health")` registers this function as the handler for `GET /health`.
- Return a plain `dict` and FastAPI serializes it to JSON automatically:
  `{"status": "ok"}`.
- Health endpoints like this are used by Kubernetes to check the app is alive
  (see the `startupProbe`/`livenessProbe`/`readinessProbe` in
  [`helm/templates/deployment.yaml`](../helm/templates/deployment.yaml)).

`GET /version` follows the same pattern, returning the version we computed earlier:

```python
@app.get("/version")
def version() -> dict[str, str]:
    return {"version": VERSION}
```

---

## 4. Reading environment variables at request time: `GET /env`

```python
@app.get("/env")
def env() -> dict[str, str]:
    return {"environment": os.environ.get("ENVIRONMENT", "unknown")}
```

Notice this reads `ENVIRONMENT` **inside** the handler, every time a request comes in.
That means changing the environment variable affects later responses without
recomputing at import time. Compare with `VERSION`, which is read once at startup.

Both approaches are valid — choose based on whether the value can change while the
app is running.

---

## 5. Validating data with Pydantic models

FastAPI uses **Pydantic** to validate and document request and response bodies.

```python
from pydantic import BaseModel

class ConfigItem(BaseModel):
    name: str
    value: str
```

This class declares that a config entry has a `name` and a `value`, both strings.
FastAPI now knows how to:

- **Parse** incoming JSON into a `ConfigItem`.
- **Reject** invalid data with an automatic `422 Unprocessable Entity` response
  (e.g. missing `value`, or `value` being a number instead of a string).
- **Document** the shape in the OpenAPI schema.

---

## 6. Handling request bodies: `POST /config`

```python
from fastapi import status

@app.post("/config", response_model=ConfigItem, status_code=status.HTTP_201_CREATED)
def set_config(item: ConfigItem) -> ConfigItem:
    """Create or update a configuration entry."""
    _config_store[item.name] = item.value
    return item
```

**Line by line:**

- `item: ConfigItem` — because the type is a Pydantic model, FastAPI reads the
  **request body** as JSON and validates it into `item`.
- `response_model=ConfigItem` — the response is validated/shaped by the same model,
  so only `name` and `value` are ever returned.
- `status_code=status.HTTP_201_CREATED` — a POST that creates a resource should
  return `201`, not the default `200`. Using the `status` constants is clearer than
  writing the raw number `201`.

The data is stored in a simple in-memory dict:

```python
_config_store: dict[str, str] = {}
```

> ⚠️ **Limitation:** this store lives in memory. It is not persisted and not shared
> across replicas — restarting the app or scaling to multiple pods loses/desyncs data.
> That's fine for a demo, but a real service would use a database or cache.

---

## 7. Path parameters and errors: `GET /config/{name}`

```python
from fastapi import HTTPException

@app.get("/config/{name}", response_model=ConfigItem)
def get_config(name: str) -> ConfigItem:
    if name not in _config_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"config '{name}' not found",
        )
    return ConfigItem(name=name, value=_config_store[name])
```

**Key ideas:**

- `{name}` in the path is a **path parameter**. FastAPI passes it to the matching
  `name: str` argument.
- To signal an error, `raise HTTPException(...)`. FastAPI turns it into a proper
  JSON error response with the right status code:
  `{"detail": "config 'x' not found"}` with HTTP `404`.
- Don't return error dicts manually with a `200` status — raise `HTTPException` so
  clients get the correct status code.

---

## 8. Deleting a resource: `DELETE /config/{name}`

```python
@app.delete("/config/{name}")
def delete_config(name: str) -> dict[str, bool]:
    if name not in _config_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"config '{name}' not found",
        )
    del _config_store[name]
    return {"deleted": True}
```

Same pattern: check existence, `404` if missing, otherwise delete and confirm.

---

## 9. Running the service

Start the development server with auto-reload:

```bash
cd app
uvicorn main:app --reload --port 8080
```

Then open the interactive, auto-generated docs:

- Swagger UI: <http://127.0.0.1:8080/docs>
- ReDoc: <http://127.0.0.1:8080/redoc>

Try the endpoints from the command line:

```bash
curl http://127.0.0.1:8080/health
# {"status":"ok"}

curl http://127.0.0.1:8080/version
# {"version":"1.0.0"}

# Create a config entry
curl -X POST http://127.0.0.1:8080/config \
  -H "Content-Type: application/json" \
  -d '{"name":"database_url","value":"postgres://example"}'

# Read it back
curl http://127.0.0.1:8080/config/database_url

# Delete it
curl -X DELETE http://127.0.0.1:8080/config/database_url
```

Set configuration through the environment:

```bash
# PowerShell
$env:ENVIRONMENT = "production"; $env:APP_VERSION = "2.1.0"
uvicorn main:app --port 8080
```

---

## 10. Testing with `TestClient`

FastAPI ships a test client (built on `httpx`) that calls your app in-process — no
running server needed. See [`test_main.py`](./test_main.py):

```python
from fastapi.testclient import TestClient
import main

client = TestClient(main.app)

def setup_function() -> None:
    # Reset the in-memory store before every test for isolation.
    main._config_store.clear()

def test_health() -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
```

**Patterns worth copying:**

- `setup_function` runs before each test, clearing shared state so tests don't leak
  into each other.
- Use `monkeypatch.setenv(...)` to test env-driven behavior (`test_env`).
- Test the full CRUD lifecycle **and** the error paths (`test_config_crud`,
  `test_config_not_found`) — 404s are behavior too.

Run the tests:

```bash
cd app
pytest -v
```

---

## 11. Packaging with Docker

The [`Dockerfile`](./Dockerfile) shows production-minded practices:

- **Multi-stage build** — dependencies are installed in a `builder` stage and copied
  into a slim runtime image, keeping the final image small.
- **Non-root user** (`appuser`, uid `10001`) — the container doesn't run as root.
- **Health checks live in Kubernetes** — rather than a Docker `HEALTHCHECK` (which the
  kubelet ignores), the `/health` endpoint is wired to the pod's
  `startupProbe`/`livenessProbe`/`readinessProbe` in the Helm deployment.
- **Explicit start command:**

```dockerfile
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

Build and run:

```bash
docker build -t devops-assessment-service ./app
docker run -p 8080:8080 -e ENVIRONMENT=docker devops-assessment-service
```

---

## 12. Recap & endpoint map

| Method | Path              | Purpose                        | Success code |
| ------ | ----------------- | ------------------------------ | ------------ |
| GET    | `/health`         | Liveness/readiness probe       | 200          |
| GET    | `/version`        | App version                    | 200          |
| GET    | `/env`            | Value of `ENVIRONMENT`         | 200          |
| POST   | `/config`         | Create/update a config entry   | 201          |
| GET    | `/config/{name}`  | Read a config entry            | 200 / 404    |
| DELETE | `/config/{name}`  | Delete a config entry          | 200 / 404    |

**Concepts you learned:**

- `@app.get/post/delete` decorators define routes.
- Returning dicts or Pydantic models produces JSON automatically.
- Pydantic `BaseModel` validates request bodies and shapes responses via
  `response_model`.
- Path parameters map from `{name}` to function arguments.
- `HTTPException` + `status` constants produce correct error responses.
- Environment variables drive configuration (`VERSION`, `ENVIRONMENT`).
- `TestClient` enables fast, in-process tests.

### Where to go next

- Add **query parameters** (e.g. `GET /config?prefix=db`) with `Query`.
- List all configs with a `GET /config` endpoint returning `list[ConfigItem]`.
- Swap the in-memory dict for a real database (SQLModel / SQLAlchemy).
- Add **async** handlers (`async def`) for I/O-bound work.
- Explore [FastAPI dependency injection](https://fastapi.tiangolo.com/tutorial/dependencies/)
  with `Depends`.

