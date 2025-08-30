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
        with open(file=path, encoding="utf-8") as f:
            for line in f:
                print("read: {data}".format(data=line.strip()))
    except FileNotFoundError:
        logger.error("File Not Found at path: {}%".format(path))
    except Exception as e:
        logger.exception(e)


if __name__ == "__main__":
    main()
