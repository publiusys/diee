# Client

`
NWORKERS=700
docker run -it --rm --name web_search_client --net host cloudsuite/web-search:client 192.168.1.20 700 --interval-min=500 --interval-max=500 --output-query-result
`

# Server

`
docker run -it --name server -v /users/hand32/index_14GB:/download/index_14GB --entrypoint=bash --net host cloudsuite/web-search:server
`