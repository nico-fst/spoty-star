docker compose down --rmi all
docker build prune -all
docker compose build --no-cache
docker compose up -d