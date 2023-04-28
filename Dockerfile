# Run RetroArch Web Player in a container
#
# docker run --rm -it -p 8080:80 retroarch-web-nightly
#
FROM debian:bullseye

LABEL maintainer "Antoine Boucher <antoine.bou13@gmail.com>"

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
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# https://github.com/libretro/RetroArch/tree/master/pkg/emscripten
# https://buildbot.libretro.com/nightly/

ENV ROOT_WWW_PATH /var/www/html

RUN cd ${ROOT_WWW_PATH}
RUN wget https://buildbot.libretro.com/nightly/emscripten/$(date -d "yesterday" '+%Y-%m-%d')_RetroArch.7z 
RUN 7z e -y $(date -d "yesterday" '+%Y-%m-%d')_RetroArch.7z 
RUN cp canvas.png media/canvas.png 
RUN chmod +x indexer 
RUN mkdir -p ${ROOT_WWW_PATH}/assets/frontend 
RUN mkdir -p ${ROOT_WWW_PATH}/assets/cores 
RUN mkdir -p ${ROOT_WWW_PATH}/assets/cores/retroarch 
RUN cd ${ROOT_WWW_PATH}/assets/frontend 
RUN wget https://buildbot.libretro.com/assets/frontend/assets.zip
RUN unzip assets.zip -d bundle 
RUN cd bundle
RUN ../../../indexer > .index-xhr 
RUN cd ${ROOT_WWW_PATH}/assets/cores 
RUN ../../indexer > .index-xhr 
RUN rm -rf ${ROOT_WWW_PATH}/RetroArch.7z 
RUN rm -rf ${ROOT_WWW_PATH}/assets/frontend/assets.zip

# Copy the download_7z_files.sh script to the container
COPY InternetArchive.sh /tmp/download_7z_files.sh

# Make the script executable and run it
RUN chmod +x /tmp/download_7z_files.sh && \
    /tmp/download_7z_files.sh

# COPY index.html ${ROOT_WWW_PATH}/index.html

RUN ../../indexer > .index-xhr

WORKDIR ${ROOT_WWW_PATH}

EXPOSE 80

COPY entrypoint.sh /

CMD [ "sh", "/entrypoint.sh"]
