
To build: 
docker build -t ml_client .
<!-- docker build --no-cache -t ml_client . -->

To run:
<!-- docker run -it ml_client -->
docker run -it --rm --network=my_network ml_client

restart db and run:
docker stop mongodb
docker rm mongodb
docker run -d --network=my_network --name=mongodb mongo:latest
docker run -it --rm --network=my_network ml_client


web-app:
docker-compose build
docker-compose up

