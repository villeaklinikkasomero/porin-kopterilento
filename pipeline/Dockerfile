# porikit: Blender (bpy) + OpenCV facade pipeline + headless Chrome for game screenshots.
# Built from the repository root:  docker build -f pipeline/Dockerfile -t porikit .
# On AWS Batch GPU instances (ECS GPU AMI) the NVIDIA driver comes from the host; Cycles uses OptiX/CUDA, Chrome uses EGL.
FROM python:3.13-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    NVIDIA_VISIBLE_DEVICES=all NVIDIA_DRIVER_CAPABILITIES=all \
    PORI_REPO=/repo PORI_HOME=/home/claude PORI_GAME=/repo PYTHONPATH=/repo/pipeline PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates wget gnupg git nodejs npm fonts-dejavu-core \
        libgl1 libegl1 libglib2.0-0 libxrender1 libxi6 libxkbcommon0 libsm6 libxxf86vm1 libxfixes3 libxext6 libx11-6 \
    && wget -q -O /tmp/chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get install -y --no-install-recommends /tmp/chrome.deb && rm /tmp/chrome.deb \
    && rm -rf /var/lib/apt/lists/*

COPY pipeline/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
RUN mkdir -p /opt/node && cd /opt/node && npm init -y >/dev/null && npm install --omit=dev puppeteer-core@25 >/dev/null
ENV NODE_PATH=/opt/node/node_modules

WORKDIR /repo
COPY . /repo
RUN ln -s /opt/node/node_modules /repo/pipeline/porikit/node_modules

RUN printf '#!/bin/sh\nexec python3 -m porikit.cli "$@"\n' > /usr/local/bin/porikit && chmod +x /usr/local/bin/porikit
CMD ["porikit", "night"]
