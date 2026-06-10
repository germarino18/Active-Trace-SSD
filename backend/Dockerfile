# Stage 1: builder — instala todas las dependencias con toolchain de build
FROM python:3.13 AS builder

WORKDIR /build
COPY . .

RUN pip install --no-cache-dir .

# Stage 2: runtime — imagen slim sin toolchain de build
FROM python:3.13-slim AS runtime

WORKDIR /app

COPY --from=builder /usr/local /usr/local
COPY --from=builder /build/app ./app/

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "app.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
