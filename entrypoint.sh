#!/bin/sh
cd ${ROOT_WWW_PATH}/assets/frontend/bundle
../../../indexer > .index-xhr
cd ${ROOT_WWW_PATH}/assets/cores
../../indexer > .index-xhr
cd ${ROOT_WWW_PATH}
nginx -g "daemon off;"
