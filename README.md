# HydroponicSystem

A CRUD application in Django that enables management hydroponic system

## Installation

1. Clone repository:
    ```bash
    git clone https://github.com/zywczak/HydroponicSystem.git
    cd HydroponicSystem
    ```

2. Build and run Docker image
    ```bash
    docker compose build
    docker compose up
    ```

3. Run tests
    ```bash
    docker exec -it hydroponicsystem-backend-1 pytest
    ```