## Installation and Running

1. Clone the repository:
    ```bash
    git clone git@github.com:DanyloSolohub/FastApi-Mongo.git
    cd your-repository
    ```

2. Make sure the `.env` file is located in the `app` folder. For example:

    ```bash
    app/.env
    ```
    You can find an example of the `.env` file in `app/.env.example`.

3. Start the containers using Docker Compose:
    ```bash
    docker-compose up --build
    ```

    This will launch the FastAPI application and the MongoDB database. FastAPI will be accessible at `http://0.0.0.0:8000`, and MongoDB will be on port `27016`.
