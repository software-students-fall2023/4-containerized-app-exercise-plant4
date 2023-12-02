Note: 
(1) I hope this can run on all platforms - not sure. I had to debug compatibility issues a lot, so it's also possible that the container just runs on apple M1 chip (hope not). Let me know if there is any issue! I'll fix the dockerfile then. 

(2) Not connected to db. For now, if u wanna test, just create a video locally, name it video.mp4, and put it in /ml_client.

To build:
docker build -t ml_client .

To run:
docker run -it --rm ml_client