FROM python:3.11

RUN apt-get update && apt-get install -y --no-install-recommends \
  ffmpeg \
  portaudio19-dev \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/swears-begone

COPY . /usr/src/swears-begone/

RUN python3 -m pip install --upgrade pip && \ 
  python3 -m pip install --break-system-packages --no-cache-dir /usr/src/swears-begone && \
  rm -rf /usr/src/swears-begone

ENTRYPOINT ["swears-begone"]