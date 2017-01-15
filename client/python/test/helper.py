import time
import docker


class Helper(object):

    def __init__(self, start=True):
        self.client = docker.from_env()
        if start:
            self.start()

    def start(self, tb_ip=8888, server_ip=8889, name="tbc_test"):
        self.container = self.client.containers.run(
            "tensorboard/api:latest",
            ports={tb_ip: tb_ip,
                   server_ip: server_ip},
            detach=True,
            name=name)
        # TODO how do we do this properly?
        time.sleep(1.5)

    def kill(self):
        self.container.kill()

    def remove(self):
        self.container.remove()
        self.container = None

    def kill_remove(self):
        # Could do with remove -f too
        self.kill()
        self.remove()
