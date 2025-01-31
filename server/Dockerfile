FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

COPY server/requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

COPY .env .env
COPY server/app.py server.py
COPY graphs/ graphs/

# RUN pip3 install --no-cache-dir -e . # what does this do? 
EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

HEALTHCHECK CMD curl --fail http://localhost:8000/health