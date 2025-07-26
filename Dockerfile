# STAGE 1: Node build

FROM node:20-alpine AS frontend-builder

WORKDIR /app/spoty-star
COPY spoty-star/package*.json ./
RUN npm install
COPY spoty-star/ .
RUN npm run build

# STAGE 2: Python Backend

FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY --from=frontend-builder /app/spoty-star/dist ./spoty-star/dist

EXPOSE 53412

CMD ["python", "-m", "backend.main"]