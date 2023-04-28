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
    git \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*
    
# Download and install the Emscripten SDK
RUN git clone https://github.com/emscripten-core/emsdk.git && \
    cd emsdk && \
    ./emsdk install 1.39.5 && \
    ./emsdk activate 1.39.5 && \
    . emsdk_env.sh

# Create the RetroArch directory and clone the required repositories
RUN mkdir ~/retroarch && \
    cd ~/retroarch && \
    git clone https://github.com/libretro/libretro-fceumm.git && \
    cd libretro-fceumm && \
    emmake make -f Makefile.libretro platform=emscripten && \
    git clone https://github.com/libretro/RetroArch.git ~/retroarch/RetroArch && \
    cp ~/retroarch/libretro-fceumm/fceumm_libretro_emscripten.bc ~/retroarch/RetroArch/dist-scripts/fceumm_libretro_emscripten.bc && \
    cd ~/retroarch/RetroArch/dist-scripts && \
    emmake ./dist-cores.sh emscripten

# Set up the environment for the RetroArch Web Player
ENV ROOT_WWW_PATH /var/www/html
COPY InternetArchive.sh /tmp/download_7z_files.sh
RUN chmod +x /tmp/download_7z_files.sh && \
    /tmp/download_7z_files.sh

COPY index.html ${ROOT_WWW_PATH}/index.html
RUN chmod +x ${ROOT_WWW_PATH}/indexer && \
    cd ${ROOT_WWW_PATH}/assets/frontend/bundle && \
    ../../../indexer > .index-xhr && \
    cd ${ROOT_WWW_PATH}/assets/cores && \
    ../../indexer > .index-xhr

# https://github.com/libretro/RetroArch/tree/master/pkg/emscripten
# https://buildbot.libretro.com/nightly/

COPY index.html ${ROOT_WWW_PATH}/index.html
RUN ../../indexer > .index-xhr
WORKDIR ${ROOT_WWW_PATH}
EXPOSE 80
COPY entrypoint.sh /
CMD [ "sh", "/entrypoint.sh"]
RUN mkdir -p ${ROOT_WWW_PATH}/assets/cores 
