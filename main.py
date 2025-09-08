import io
import os
import socket
import sys
from typing import Callable, Generator, Optional, Union

from tcp_to_http import logger


def get_lines_from_reader(stream: Union[io.FileIO, socket.SocketIO, socket.socket]) -> Generator[str, None, None]:
    r"""
    Incrementally read text lines from a binary stream or socket.

    The function consumes bytes from the given stream-like object in
    small chunks, accumulates them in a buffer, and yields decoded
    lines one at a time when a newline character is encountered.

    :param reader: io.FileIO or socket.SocketIO or socket.socket
        A file-like object with a ``.read(size) -> bytes`` method, or
        a socket-like object with a ``.recv(size) -> bytes`` method.

    :yield: str
        Decoded lines of text without trailing newline characters.

    """
    # if not (isinstance(f, io.FileIO) or isinstance(f, socket.SocketIO) or isinstance(f, socket.socket)):
    #     raise ValueError("Invalid file or connection type provided!")

    reader: Optional[Callable[[int], bytes]] = getattr(stream, "read", None)
    receiver: Optional[Callable[[int], bytes]] = getattr(stream, "recv", None)
    # If f has a .read(), reader is a bound method (callable: reader(n) -> bytes). If not, it’s None.
    # Similarly, the TCP connection object exposes `conn.recv()` method to read the bytes sent
    # if you have passed the connection object as the stream. (See `get_from_conn()` method for more)
    # So their types are “either a callable that returns bytes, or None.

    if not reader and not receiver:
        raise ValueError("Need .read() or .recv()")

    try:
        buffer = bytearray()
        while True:
            # Read 8 bytes at a time
            # chunk = f.read(8) if isinstance(f, io.FileIO) else f.recv(8)
            chunk = reader(8) if reader else receiver(8)
            if not chunk:  # EOF reached
                # Files: .read() returns b'' at EOF
                # TCP: .recv() returns b'' when the peer cleanly closes
                break

            buffer.extend(chunk)
            # Emit as many complete lines in buffer
            while True:
                new_line = buffer.find(b"\n")
                if new_line == -1:  # Returns -1 if it cannot find the character in the buffer
                    break

                line_bytes = buffer[:new_line]
                # Strip out any carriage return character
                if line_bytes.endswith(b"\r"):
                    line_bytes = line_bytes[:-1]

                yield line_bytes.decode()

                # Drop emitted line + '\n' from the accumulator
                del buffer[: new_line + 1]

        # Read the last line if present
        if buffer:
            if buffer.endswith((b"\r")):
                buffer = buffer[:-1]
            yield buffer.decode()
        return
    except Exception as e:
        logger.exception(e)


def read_data_from_file(file_path: str):
    """Read data line by line from a file."""
    try:
        with open(file=file_path, mode="rb", buffering=0) as f:
            f: io.FileIO
            for line in get_lines_from_reader(stream=f):
                print("read:", line)
    except FileNotFoundError:
        logger.error("File Not Found at path: {}".format(file_path))
        sys.exit(0)


# Socket Programming:
# https://realpython.com/python-sockets/
# https://youtu.be/3QiPPX-KeSc?si=W92KcIUbOqSChcLi
# https://docs.python.org/3/library/socket.html

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 42069  # Port to listen on (non-privileged ports are > 1023)


def receive_data_from_tcp_conn():
    """
    Receive data line by line from a TCP Connection.

    How to run:

    1. Run `uv run main.py`
    2. In another terminal run `cat messages.txt | nc -w 1 127.0.0.1 42069`
    3. If the it ran successfully, the terminal running the python script should have received the data.
    """
    with socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()  # <-- BLOCKS until a client connects
        # with conn:
        #     logger.info(f"Connected by {addr=}")
        #     for line in get_lines_from_reader(stream=conn):
        #         print("read:", line)

        # conn.makefile() supports IO operations like `f.read()` instead of conn.recv()^^^ like above
        with conn.makefile(mode="rb", buffering=0) as raw_bytes:
            logger.info(f"Connected by {addr=}")
            for line in get_lines_from_reader(stream=raw_bytes):
                print("read:", line)



def main():
    # path = os.curdir + "/messages.txt"
    # read_data_from_file(file_path=path)

    receive_data_from_tcp_conn()


if __name__ == "__main__":
    main()
