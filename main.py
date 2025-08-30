import logging
import os

formatter = logging.Formatter(
    # fmt="%(asctime)s | %(levelname)s | %(filename)s:%(lineno)s | %(name)s:%(funcName)s | %(message)s",
    fmt="%(levelname)s: %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%SZ",
)
handler = logging.StreamHandler()
handler.setFormatter(fmt=formatter)
handler.setLevel(level=logging.INFO)
logger = logging.getLogger(name=__name__)
logger.addHandler(handler)


def main() -> None:
    path = os.curdir + "/messages.txt"
    try:
        # Read file line by line
        with open(file=path) as f:
            while True:
                line = f.readline().strip()
                if not line:
                    # returns an empty string
                    break
                print("read: {data}".format(data=line))
    except FileNotFoundError:
        logger.error("File Not Found at path: {}%".format(path))
    except Exception as e:
        logger.exception(e)


if __name__ == "__main__":
    main()
