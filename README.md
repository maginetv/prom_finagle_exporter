# janitor-node

janitor node to run local tasks on hosts like docker cleanup


#### start service
```bash
$ gunicorn .app:api
```

in docker
```bash
sudo docker run --privileged -d \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v /usr/bin/docker:/usr/bin/docker \
    docker-repo.tvoli.com:2376/alpine/dind/janitor-node
```


#### Build docker images
build alpine janitor-node image
```bash
$ docker build -t docker-repo.tvoli.com:2376/alpine/dind/janitor-node .
```

push alpine janitor-node
```bash
$ docker push docker-repo.tvoli.com:2376/alpine/dind/janitor-node
```


#### Deploy
this will deploy service janitor-node to all nodes in test com
```bash
$ ./deploy.py deploy -e test-com_eu-west-1 -s janitor-node  -n all
```
