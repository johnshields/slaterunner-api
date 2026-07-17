FROM node:22-slim AS app-build

WORKDIR /build
COPY app/package*.json app/
RUN npm --prefix app ci
COPY app app
RUN npm --prefix app run build


FROM python:3.14-slim

WORKDIR /srv/api
COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api /srv/api
COPY --from=app-build /build/app/dist /srv/app/dist

EXPOSE 8000
CMD ["python", "-m", "uvicorn", "main:app", "--app-dir", "src", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips", "*"]
