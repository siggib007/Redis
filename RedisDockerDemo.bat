docker run -p 6379:6379 --name some-redis -d redis
py RedisDemo.py
docker rm -f some-redis