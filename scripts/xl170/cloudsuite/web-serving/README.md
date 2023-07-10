# Client

```
QPS=20

docker run -d -it --entrypoint /bin/bash --net=host --name=faban_client cloudsuite/web-serving:faban_client
```

# Server

```
docker run -d -it --net=host --name=database_server cloudsuite/web-serving:db_server

docker run -dt --net=host --name=memcache_server cloudsuite/web-serving:memcached_server

docker run -dt --net=host --name=web_server cloudsuite/web-serving:web_server /etc/bootstrap.sh http 192.168.1.20 192.168.1.20 192.168.1.20 40 1
```
