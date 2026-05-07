# --- Builder ---
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /build

COPY pyproject.toml .
COPY src/ ./src/

RUN pip install --upgrade pip && \
  pip install --no-cache-dir --prefix=/install . --break-system-packages

# --- Runtime ---
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ENV XDG_CACHE_HOME=/models
RUN mkdir -p /models && chmod 777 /models

WORKDIR /app

COPY --from=builder /install/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /install/bin /usr/local/bin

COPY --from=mwader/static-ffmpeg:8.1 /ffmpeg /usr/local/bin/
COPY --from=mwader/static-ffmpeg:8.1 /ffprobe /usr/local/bin/

ENTRYPOINT ["swears-begone"]