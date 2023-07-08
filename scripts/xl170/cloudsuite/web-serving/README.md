# Client

`
QPS=20
docker run --net=host --name=faban_client_20 cloudsuite/web-serving:faban_client 192.168.1.20 20
`

# Server

`
docker run -d -it --net=host --name=database_server cloudsuite/web-serving:db_server
docker run -dt --net=host --name=memcache_server cloudsuite/web-serving:memcached_server
docker run -dt --net=host --name=web_server cloudsuite/web-serving:web_server /etc/bootstrap.sh http 192.168.1.20 192.168.1.20 192.168.1.20 40 1
`