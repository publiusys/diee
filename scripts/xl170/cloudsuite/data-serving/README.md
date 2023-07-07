# Client

`
docker run -d -t -i --name cassandra-client --net host cloudsuite/data-serving:client bash
`

# Server

`
docker run -d --name cassandra-server --net host cloudsuite/data-serving:server --listen-ip=192.168.1.20 --reader-count=10 --writer-count=80
`