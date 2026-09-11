# DevOps Engineer Homework

## Overview

The goal of this assignment is to evaluate how you approach a typical DevOps engineering task involving:

- Application development / scripting
- Containerization
- Kubernetes
- Helm
- Terraform
- CI/CD
- Code review

The repository contains intentionally incomplete and imperfect components.
Your task is to complete, improve and document the solution.

You are not expected to produce a perfect production-ready system. We are more interested in your engineering approach, decision-making and ability to balance quality with the time constraints.

Time limit: approximately **3 hours**

## Repository Contents

The repository contains:

- An incomplete application skeleton
- Terraform configuration requiring review and improvement
- An incomplete Helm chart
- An incomplete CI/CD pipeline

Your task is to complete and improve these components. Our goal is to understand your engineering approach, and we will build the upcoming technical interview on this project.

## Goal 1

Complete and improve the provided project.

The repository contains the following files:

- Incomplete application code
- Broken/incomplete terraform configuration
- Incomplete Helm Chart
- Incomplete Gitlab CI pipeline

### Requirements

#### Application

Implement a simple application in either:

- Go
- Python

The application must expose the following endpoints:

##### `GET /health`

**Response:**

```json
{
    "status": "ok"
}
```

##### `GET /version`

**Response:**

```json
{
    "version": "1.0.0"
}
```

##### `GET /env`

**Response:**

```json
{
    "environment": "<value from ENVIRONMENT variable>"
}
```

##### `POST /config`

**Request:**

```json
{
    "name": "database_url",
    "value": "postgres://example"
}
```

**Response:**

```json
{
    "name": "database_url",
    "value": "postgres://example"
}
```

##### `GET /config/{name}`

**Example:**

```bash
GET /config/database_url
```

**Response:**

```json
{
    "name": "database_url",
    "value": "postgres://example"
}
```

##### `DELETE /config/{name}`

**Response:**

```json
{
    "deleted": true
}
```

#### Containerization

- Create the necessary Dockerfile with minimal setup
- The image should:
  - build successfully
  - run locally
  - expose the application endpoint

#### Terraform

- Review and fix/complete the Terraform code
- The Terraform code contains several issues and areas for improvement
- In case you don't get time to implement changes describe what would you still improve and why
- Document any changes you make

#### Helm

- Review and fix/complete the Helm Chart
- The chart should deploy the application to Kubernetes
- Document any change you make

#### Gitlab CI

- Complete the pipeline so it becomes capable of building and deploying the application
- The pipeline should support the workflow required to build and deploy the application
- The pipeline should be logically complete and demonstrate how you would automate the process
- Add any other necessary jobs to the pipeline

#### Documentation

Update the project README with following information.

## What You Changed
**Note: Due to the short amount of time AI was used to research and type code instead of me**
All planning, verification and testing was done by "hand".

- Application (`app/`) — Implemented the FastAPI service with all six
  required endpoints, a Pydantic model for `/config`, proper `404` handling and a
  SQLite-backed config store persisted to disk. Added requirements.txt, dev dependencies and unit tests. 
  Rationale:
  FastAPI gives validation and typing with minimal code; SQLite (stdlib, no extra
  dependency) makes the store survive restarts when placed on a persistent volume.

- Persistence (Helm/K8s) — Added a `PersistentVolumeClaim` template and wired it into the Deployment: 
  mounted at "/data", exposed to the app via `CONFIG_DB_PATH`, with `strategy: Recreate` and
  "fsGroup: 10001" so every user can write to the volume.

- Containerization — Added a multi-stage Dockerfile with slim base, non-root user
  and exposed on 8080 port. Rationale: small, easily reproducible image.

- Terraform — **Due to little to no terraform knowledge, AI was heavly involved in this part** 
  Fixed the broken main.tf: empty image.tag, unquoted prod.
  Corrected the chart path to helm, replaced the hardcoded namespace with a variable. 
  Added "required_providers" with version pins, gave variables descriptions
  and defaults, and populated "outputs.tf".

- Helm — Fixed name mismatches, corrected the container port, 
  added _helpers.tpl with standard labels/selectors, templated all resources, added liveness/readiness probes, 
  resources and ingressClassName, and expanded on values.yaml.
  
- GitLab CI — Replaced the placeholder echo jobs with real stages.
  Connected all code quality related stages into parallel for quicker run.
  
  Kaniko image build/push to the GitLab registry,
  Helm packaging as an artifact and a manual Helm-based deploy job.

## Assumptions
- Base Idea - During the first interview, the interviewer told me of future projects,
  such as rewriting cash register apps, supply line program and possibly webshop.
  As I'm not familiar with the first two, I did some research and tried to tailor
  the homework based on the things I found.
  A supply line application is distributed accross many stakeholders, must be visible and secure,
  - Python: I know/like python much better than go. In k8s environments, go is the more accepted programming language.
  - FastAPI: Python ecosystem, async model for parallel traffic, Pydantic for validation
  - Docker: As mentioned before, small, easily recreatable base image
  - K8s/Helm: Scaling, health checks, perfect environment for multiservice based apps.
    (Although implementing scaling did not fit into the timeframe)
  - GitlabCI: Commit validation, parallel code quality checks, branch gated deployment.
    (GitlabCI is a good git native system, but IMO jenkins is the ace for this job)

## Known Limitations
- Database SQLite on a single `ReadWriteOnce` volume.
  Data survives pod restarts, but the store does not scale, and the cluster recreates the DB on every change. 
  A Postgres DB would be much much better in terms of scaling and accessibility.
- The CI deploy job is manual and assumes a runner with cluster access; no cloud
  deployment is configured (per the assignment).
- No secret management, autoscaling or network policies are configured. Security-wise this is a bad system.

## Production Improvements
- Replace SQLite with a networked, replicated backend (Postgres) and add schema migrations.
- Add cert-manager, externalized secrets (jenkins is perfect to store these in environment) and network policies.
- Add observability: structured logging, Prometheus metrics, tracing and dashboards.
- Introduce a remote Terraform backend with state locking and environment workspaces.
- Introduce security measures: image hardening, Blackduck scan
- Before deployment, a Terraform Plan step could sieve issues arising after/upon deploy.
- Code quality checks could improve with specific tool involvements (Sonar)
- E2E Test pipeline after deploy.
