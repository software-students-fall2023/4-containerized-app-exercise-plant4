To run:
docker-compose -f tests/docker-compose.test.yml up --build

docker build -t mypytestcontainer -f tests/Dockerfile.test .
docker run mypytestcontainer

