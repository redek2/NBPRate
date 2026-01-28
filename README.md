# NBPRate

Application for retrieving and visualizing currency exchange rates from the National Bank of Poland (NBP) API. The system allows users to view data broken down by years, quarters, months, and days. The project emphasizes strict architectural separation, containerization, and Behavior-Driven Development (BDD).

## Technology Stack

* **Frontend:** Angular (served via Nginx)
* **Backend:** Python 3.13 + FastAPI
* **Database:** PostgreSQL 16
* **Infrastructure:** Docker & Docker Compose
* **Testing:** Pytest (Backend), Jasmine/Karma (Frontend)

## Prerequisites

* Docker Desktop (or Docker Engine + Docker Compose Plugin)
* Git

## Project Architecture

The application is composed of three isolated containers orchestrated via Docker Compose:

1.  **db**: PostgreSQL 16 database with persistent volume storage.
2.  **backend**: FastAPI application running on Uvicorn.
3.  **frontend**: Angular application built for production and served by Nginx.

## Getting Started

### 1. Clone the repository
```bash
git clone <repository_url>
cd NBPRate
```
### 2. Environment Configuration
Create a .env file in the root directory. This file is excluded from version control for security reasons. Define the following variables:
```
POSTGRES_DB=nbp_db
POSTGRES_USER=nbp_user
POSTGRES_PASSWORD=your_secure_password
```
### 3. Build and run
Start the entire infrastructure using Docker Compose:
```
docker-compose up --build
```
To run in detached mode:
```
docker-compose up -d
```
### 4. Stopping the Application
To stop containers and remove network artifacts:
```
docker-compose down
```

## Access Points
| Service | URL / Port | Description |
| :--- | :--- | :--- |
| Frontend | http://localhost:4200 | Main User Interface |
| Backend API | http://localhost:8000 | API Root |
| API Documentation | http://localhost:8000/docs | Swagger UI (OpenAPI) |
| Database | localhost:5432 | Direct PostgreSQL access (Host mapping) |