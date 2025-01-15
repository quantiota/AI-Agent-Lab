import docker

client = docker.DockerClient(base_url='unix://var/run/docker.sock')
