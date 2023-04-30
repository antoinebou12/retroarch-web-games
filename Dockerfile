# Run RetroArch Web Player in a container
#
# docker run --rm -it -d -p 8080:80 retroarch-web-nightly
#

# Stage 1: Builder
FROM debian:bullseye AS builder

LABEL maintainer="Antoine Boucher <antoine.bou13@gmail.com>"

# Install required packages
RUN apt-get update && apt-get install -y \
    ca-certificates \
    unzip \
    sed \
    p7zip-full \
    coffeescript \
    xz-utils \
    nginx \
    wget \
    vim \
    parallel \
    git \
    python3 \
    python3-pip \
    lbzip2 \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Download and install RetroArch Web Player
ENV ROOT_WWW_PATH /var/www/html
RUN cd ${ROOT_WWW_PATH} 
RUN wget https://buildbot.libretro.com/nightly/emscripten/$(date -d "yesterday" '+%Y-%m-%d')_RetroArch.7z
RUN 7z x -y $(date -d "yesterday" '+%Y-%m-%d')_RetroArch.7z
RUN mv retroarch/* .
RUN rmdir retroarch 
RUN sed -i '/<script src="analytics.js"><\/script>/d' ./index.html
RUN mkdir -p ${ROOT_WWW_PATH}/assets/frontend/bundle
RUN chmod +x indexer
RUN mkdir -p ${ROOT_WWW_PATH}/assets/cores
RUN cd ${ROOT_WWW_PATH}/assets/frontend/bundle
RUN ../../../indexer > .index-xhr
RUN cd ${ROOT_WWW_PATH}/assets/cores
RUN ../../indexer > .index-xhr
RUN rm -rf ${ROOT_WWW_PATH}/RetroArch.7z

# Install Python dependencies for InternetArchive script
COPY InternetArchive.py /tmp/InternetArchive.py
RUN pip3 install requests typer rich

# Run the InternetArchive script
RUN chmod +x /tmp/InternetArchive.py && \
    python3 /tmp/InternetArchive.py

# Set up the environment for the RetroArch Web Player
WORKDIR /var/www/html
# COPY index.html /var/www/html/index.html
EXPOSE 80
COPY entrypoint.sh /
CMD ["sh", "/entrypoint.sh"]
