FROM python:3.11-slim

RUN apt-get update && apt-get install -y curl build-essential \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g npm@latest \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

RUN cd judd && npm ci

RUN pip install --no-cache-dir . -v

RUN touch .env

# uses default
EXPOSE 5000

CMD ["splatnet"]