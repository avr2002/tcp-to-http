"""
Learned about:

1. File Descriptors
2. `os.open()` is much low-level operation that using built-in `open()` method in Python
"""

import logging
import os
import sys

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


# fd = file descriptor
# What is a File Descriptor? - https://en.wikipedia.org/wiki/File_descriptor
# More:
# - https://docs.python.org/3/library/os.html#os.open
# - https://docs.python.org/3/library/os.html#os.close
# - https://stackoverflow.com/questions/15039528/what-is-the-difference-between-os-open-and-os-fdopen
def main() -> None:
    path = os.curdir + "/messages.txt"
    fd = os.open(path, flags=os.O_RDONLY)  # os.O_RDONLY -- Open the file as ReadOnly
    # os.O_WRONLY: Write only; os.O_RDWR: Read & write, os.O_CREAT: Create if not exist.
    try:
        # Read the data 8 bytes at a time
        while True:
            data = os.read(fd, 8).decode("utf-8")
            if not data:
                # At the end of file returns an empty string
                break
            print("read: {data}".format(data=data))
    except FileNotFoundError:
        logger.error("File Not Found at path: {}%".format(path))
        sys.exit(0)
    except Exception as e:
        logger.exception(e)
    finally:
        os.close(fd)


if __name__ == "__main__":
    main()
