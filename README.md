### google chrome cdp command
# Linux
google-chrome \
  --remote-debugging-port=9222 \
  --user-data-dir=/tmp/chrome-debug



### Docker
docker stop chrome && docker rm chrome

docker run -d --name chrome --shm-size=2gb -p 9223:9223 chrome-cdp



# Try curl from INSIDE the container
docker exec chrome curl -s http://localhost:9223/json/version
