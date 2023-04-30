#!/bin/bash

ROOT_WWW_PATH=$1

cd ${ROOT_WWW_PATH} \
	&& wget https://buildbot.libretro.com/nightly/emscripten/$(date -d "yesterday" '+%Y-%m-%d')_RetroArch.7z \
	&& 7z x -y $(date -d "yesterday" '+%Y-%m-%d')_RetroArch.7z \
	&& mv retroarch/* . \
	&& rmdir retroarch \
	&& sed -i '/<script src="analytics.js"><\/script>/d' ./index.html \
	&& chmod +x indexer \
	&& mkdir -p ${ROOT_WWW_PATH}/assets/cores \
	&& cd ${ROOT_WWW_PATH}/assets/frontend/bundle \
	&& ../../../indexer > .index-xhr \
	&& cd ${ROOT_WWW_PATH}/assets/cores \
	&& ../../indexer > .index-xhr \
	&& rm -rf ${ROOT_WWW_PATH}/RetroArch.7z \
	&& rm -rf ${ROOT_WWW_PATH}/assets/frontend/bundle.zip
