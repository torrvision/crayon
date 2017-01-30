import time
import requests
try:
    import docker
except:
    RuntimeError("Please run 'pip install docker' before using this module.")

class Helper(object):

    def __init__(self, start=True):
        self.client = docker.from_env()
        if start:
            self.start()

    def start(self, tb_ip=8888, server_ip=8889, name="crayon"):
        self.container = self.client.containers.run(
            "alband/crayon:latest",
            ports={tb_ip: tb_ip,
                   server_ip: server_ip},
            detach=True,
            name=name)
        # check server is working
        running = False
        retry = 40
        while not running:
            try:
                assert(requests.get("http://localhost:"+str(server_ip)).ok)
                running = True
            except:
                retry -= 1
                if retry == 0:
                    # The test will trigger the not running server error
                    return
                time.sleep(0.1)

    def kill(self):
        self.container.kill()

    def remove(self):
        self.container.remove()
        self.container = None

    def kill_remove(self):
        # Could do with remove -f too
        self.kill()
        self.remove()
