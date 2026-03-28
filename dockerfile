FROM python:3.11-slim

RUN apt-get update && apt-get install -y curl build-essential \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g npm@latest \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY judd/package.json judd/package-lock.json ./judd/

RUN cd judd && npm ci

COPY . .

RUN pip install --no-cache-dir . -v

RUN touch .env

EXPOSE 5000

CMD ["splatnet"]