# Client

```
docker run -d -t -i --name cassandra-client --net host cloudsuite/data-serving:client bash

docker exec cassandra-client ./warmup.sh 192.168.1.20 10000000 10

docker exec cassandra-client ./load.sh 192.168.1.20 10000000 10000 10 300000
```

# Server

`
docker run -d --name cassandra-server --net host cloudsuite/data-serving:server --listen-ip=192.168.1.20 --reader-count=10 --writer-count=80
`
