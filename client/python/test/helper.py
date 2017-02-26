import time
import requests
try:
    import docker
except:
    RuntimeError("Please run 'pip install docker' before using this module.")


class Helper(object):

    def __init__(self, start=True, tb_ip=8888, server_ip=8889, name="crayon"):
        self.client = docker.from_env()
        self.tb_ip = tb_ip
        self.server_ip = server_ip
        self.name = name
        if start:
            self.start()

    def start(self):
        self.container = self.client.containers.run(
            "alband/crayon:latest",
            ports={8888: self.tb_ip,
                   8889: self.server_ip},
            detach=True,
            name=self.name)
        # check server is working
        running = False
        retry = 50
        while not running:
            try:
                assert(
                    requests.get("http://localhost:" + str(self.server_ip)).ok
                )
                running = True
            except:
                retry -= 1
                if retry == 0:
                    # The test will trigger the not running server error
                    return
                time.sleep(0.1)

    def kill(self):
        if hasattr(self, "container"):
            self.container.kill()

    def remove(self):
        if hasattr(self, "container"):
            self.container.remove()
            self.container = None

    def kill_remove(self):
        # Could do with remove -f too
        self.kill()
        self.remove()
