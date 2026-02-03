# Building with Docker

Rename `.env.example` to `.env` and edit with the appropriate variables.

## Running

### Production

```bash
git pull
docker compose up -d --build
```

### Development

```bash
docker compose -f docker-compose.dev.yml up -d --build
npm start
```
