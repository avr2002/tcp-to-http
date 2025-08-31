import logging
import mmap
import os
import sys
from typing import Generator

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


def read_lines(fpath: str) -> Generator[str, None, None]:
    """Stream a text file line-by-line using raw OS syscalls (`os.open`/`os.read`) with low allocation overhead."""
    fd = None
    try:
        fd = os.open(fpath, flags=os.O_RDONLY)
        buffer = bytearray()
        while True:
            # Read 8 bytes at a time
            chunk = os.read(fd, 8)
            if not chunk:  # EOF reached
                break

            buffer.extend(chunk)
            # Emit as many complete lines in buffer
            while True:
                nl = buffer.find(b"\n")  # new-line
                if nl == -1:
                    break

                line_bytes = buffer[:nl]
                if line_bytes.endswith(b"\r"):
                    line_bytes = line_bytes[:-1]

                # print("read:", line_bytes.decode())
                yield line_bytes.decode()

                # Drop emitted line + '\n' from the accumulator
                del buffer[: nl + 1]

        # Read the last line if present
        if buffer:
            if buffer.endswith((b"\r")):
                buffer = buffer[:-1]
            # print("read:", buffer.decode())
            yield buffer.decode()

    except FileNotFoundError:
        logger.error("File Not Found at path: {}".format(fpath))
        sys.exit(0)
    except Exception as e:
        logger.exception(e)
    finally:
        if fd:
            os.close(fd)


def main():
    path = os.curdir + "/messages.txt"
    for line in read_lines(fpath=path):
        print("read:", line, end="\n")


if __name__ == "__main__":
    main()
