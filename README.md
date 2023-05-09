# Retroarch Web with Installed Games
This repository provides a self-hosted RetroArch web player with a collection of games for NES, SNES, Genesis, and Gameboy. Run the Docker image to quickly set up and host your own RetroArch web player and enjoy classic games on your browser.

## Features
### Pre-loaded games for:
- NES
- SNES
- Genesis
- Gameboy
### Self-hosted web player
### Docker container for easy deployment

## Image Size
### Warning 
The Docker image size is approximately 10GB due to the inclusion of various games.

How to use this image :
You can run this image like this:

https://hub.docker.com/repository/docker/antoine13/retroarch-web-games

```
docker-compose up -d
```

After the container is up and running, open your web browser and navigate to http://localhost:8080 to start using the RetroArch web player.

## Acknowledgements
This Docker image is based on:

- [Inglebard/dockerfiles (retroarch-web branch)](https://github.com/Inglebard/dockerfiles/tree/retroarch-web)
- [libretro/RetroArch (master/pkg/emscripten)](https://github.com/libretro/RetroArch/tree/master/pkg/emscripten)

## License
This project is licensed under the MIT License.
