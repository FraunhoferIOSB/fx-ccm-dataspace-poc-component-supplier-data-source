# FX Data Generator / Component Supplier Data Source

## Installation

### Requirements

- Python 3.10.11
- pip

Install required packages:

```bash
pip install -r req.txt
 ```

## Run application with FastAPI

FastAPI:

```bash
uvicorn app.datagenerator:app --host 0.0.0.0 --port 80
```

## Build Docker Container

Build Docker-Image:

```bash
docker build -t fx_data_generator .
```

Run the Docker-Container:

```bash
docker run -d -p 80:80 fx_data_generator
```


