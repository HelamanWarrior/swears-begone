FROM python:3.9

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ffmpeg portaudio19-dev

RUN python3 -m pip install --upgrade pip

# Python installation
WORKDIR /usr/src/app

RUN pip3 install whisper-timestamped

# Expose default workdir for mounting audio files
VOLUME /audio

# Set entrypoint to Python module
ENTRYPOINT ["whisper_timestamped"]
