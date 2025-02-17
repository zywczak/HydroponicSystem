# HydroponicSystem

A CRUD application in Django that enables management hydroponic system

## Installation

1. Clone repository:
    ```bash
    git clone https://github.com/zywczak/HydroponicSystem.git
    cd HydroponicSystem
    ```

2. Add .env file:
    - db.env  --> in folder with docker-compose.yml. Example:
    ```bash
    POSTGRES_PASSWORD=postgres
    POSTGRES_USER=postgres
    POSTGRES_DB=postgres
    ```
    - .env  --> in folder with Dockerfile. Example:
    ```bash
    DB_NAME=postgres
    DB_USER=postgres
    DB_PASSWORD=postgres
    DB_HOST=db
    DB_PORT=5432

    SECRET_KEY=
    ```
    - ```SECRET_KEY=``` *(generate using the following command:)*  

    ```bash
    python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

    ```


3. Build and run Docker image
    ```bash
    docker compose build
    docker compose up
    ```

4. Run tests
    ```bash
    docker exec -it hydroponicsystem-backend-1 pytest
    ```

## Address API:
 [http://localhost:8000/](http://localhost:8000)

 ## Dokumentation:
 [http://localhost:8000/api/schema/swagger-ui/](http://localhost:8000/api/schema/swagger-ui)

 and in code