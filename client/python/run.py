from tensorboard_http_api.tbclient import TBClient
import json
import time


def main():
    tbc = TBClient("localhost", 8889)
    print(tbc.get_experiments())
    data = [[time.clock(), 1, 3]]
    tbc.add_scalar("foo", "bar", data[0])
    print(tbc.get_experiments("foo"))


if __name__ == "__main__":
    main()
