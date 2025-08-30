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


# fd = file descriptor
# What is a File Descriptor? - https://en.wikipedia.org/wiki/File_descriptor
# More:
# - https://docs.python.org/3/library/os.html#os.open
# - https://docs.python.org/3/library/os.html#os.close
# - https://stackoverflow.com/questions/15039528/what-is-the-difference-between-os-open-and-os-fdopen
def main() -> None:
    path = os.curdir + "/messages1.txt"
    fd = None
    try:
        fd = os.open(path, flags=os.O_RDONLY)  # os.O_RDONLY -- Open the file as ReadOnly
        # os.O_WRONLY: Write only; os.O_RDWR: Read & write, os.O_CREAT: Create if not exist.
        # Read the data 8 bytes at a time
        while True:
            data = os.read(fd, 8).decode("utf-8")
            if not data:
                break
            print("read: {data}".format(data=data))
    except FileNotFoundError:
        logger.error("File Not Found at path: {}%".format(path))
    except Exception as e:
        logger.exception(e)
    finally:
        if fd:
            os.close(fd)


if __name__ == "__main__":
    main()
