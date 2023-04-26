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
RUN cd ${ROOT_WWW_PATH}/assets/frontend/bundle 
RUN ../../../indexer > .index-xhr 
RUN cd ${ROOT_WWW_PATH}/assets/cores 
RUN wget -m -np -c -U "/var/www/html/assets/cores/NES/eye01" -R "index.html*" "https://the-eye.eu/public/rom/NES/"  
RUN wget -m -np -c -U "/var/www/html/assets/cores/SNES/eye01" -R "index.html*" "https://the-eye.eu/public/rom/SNES/" 
RUN wget -m -np -c -U "/var/www/html/assets/cores/GB/eye01" -R "index.html*" "https://the-eye.eu/public/rom/Nintendo%20Gameboy/"  
RUN wget -m -np -c -U "/var/www/html/assets/cores/GBA/eye01" -R "index.html*" "https://the-eye.eu/public/rom/Nintendo%20Gameboy%20Advance/" 
RUN wget -m -np -c -U "/var/www/html/assets/cores/GBC/eye01" -R "index.html*" "https://the-eye.eu/public/rom/Nintendo%20Gameboy%20Color/"  
RUN wget -m -np -c -U "/var/www/html/assets/cores/SegaGenesis/eye01" -R "index.html*" "https://the-eye.eu/public/rom/Sega%20Genesis/" 
RUN ../../indexer > .index-xhr 
RUN rm -rf ${ROOT_WWW_PATH}/RetroArch.7z 
RUN rm -rf ${ROOT_WWW_PATH}/assets/frontend/assets.zip
	
COPY sort_mkdir.sh ${ROOT_WWW_PATH}/assets/cores/the-eye.eu/public/rom/
RUN mv ${ROOT_WWW_PATH}/assets/cores/the-eye.eu/public/rom/Nintendo\ Gameboy/ ${ROOT_WWW_PATH}/assets/cores/the-eye.eu/public/rom/NintendoGameboy 
RUN mv ${ROOT_WWW_PATH}/assets/cores/the-eye.eu/public/rom/Nintendo\ Gameboy\ Advance/ ${ROOT_WWW_PATH}/assets/cores/the-eye.eu/public/rom/NintendoGameboyAdvance 
RUN mv ${ROOT_WWW_PATH}/assets/cores/the-eye.eu/public/rom/Nintendo\ Gameboy\ Color/ ${ROOT_WWW_PATH}/assets/cores/the-eye.eu/public/rom/NintendoGameboyColor 
RUN mv ${ROOT_WWW_PATH}/assets/cores/the-eye.eu/public/rom/Sega\ Genesis/ ${ROOT_WWW_PATH}/assets/cores/the-eye.eu/public/rom/SegaGenesis 
RUN bash ${ROOT_WWW_PATH}/assets/cores/the-eye.eu/public/rom/sort_mkdir.sh ${ROOT_WWW_PATH}/assets/cores/the-eye.eu/public/rom/NES/ 
RUN bash ${ROOT_WWW_PATH}/assets/cores/the-eye.eu/public/rom/sort_mkdir.sh ${ROOT_WWW_PATH}/assets/cores/the-eye.eu/public/rom/SNES/ 
RUN bash ${ROOT_WWW_PATH}/assets/cores/the-eye.eu/public/rom/sort_mkdir.sh ${ROOT_WWW_PATH}/assets/cores/the-eye.eu/public/rom/NintendoGameboy/ 
RUN bash ${ROOT_WWW_PATH}/assets/cores/the-eye.eu/public/rom/sort_mkdir.sh ${ROOT_WWW_PATH}/assets/cores/the-eye.eu/public/rom/NintendoGameboyAdvance/ 
RUN bash ${ROOT_WWW_PATH}/assets/cores/the-eye.eu/public/rom/sort_mkdir.sh ${ROOT_WWW_PATH}/assets/cores/the-eye.eu/public/rom/NintendoGameboyColor/ 
RUN bash ${ROOT_WWW_PATH}/assets/cores/the-eye.eu/public/rom/sort_mkdir.sh ${ROOT_WWW_PATH}/assets/cores/the-eye.eu/public/rom/SegaGenesis/ 
RUN cd ${ROOT_WWW_PATH}/assets/cores 
RUN ../../indexer > .index-xhr

COPY index.html ${ROOT_WWW_PATH}/index.html

RUN cd ${ROOT_WWW_PATH}/assets/cores \
   && ../../indexer > .index-xhr

WORKDIR ${ROOT_WWW_PATH}

EXPOSE 80

COPY entrypoint.sh /

CMD [ "sh", "/entrypoint.sh"]
