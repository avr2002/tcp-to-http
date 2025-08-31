import logging
import mmap
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


def read_lines(fpath: str) -> None:
    """Using standard Python's built-in `open()` method."""
    try:
        # Read file line by line
        with open(file=fpath, encoding="utf-8") as f:
            for line in f:
                print("read: {data}".format(data=line.strip()))
    except FileNotFoundError:
        logger.error("File Not Found at path: {}".format(fpath))
    except Exception as e:
        logger.exception(e)


# The `f.readinto()`` method in Python is a method available on file-like objects, especially those
# representing binary streams, that allows reading data directly into a pre-allocated, mutable buffer object.
# Instead of returning a new bytes object, `readinto()`` fills the provided buffer directly, avoiding an extra copy operation.
def read_file_with_manual_buffer_v1(fpath: str) -> None:
    r"""
    Read a text file "line by line" using low-level, manual buffering on a fixed-size bytearray.

    Overview
    --------
    This implementation demonstrates how to stream a file without relying on the file
    object's iterator (`for line in f:`). It:
      • Preallocates a mutable `bytearray` and fills it with `readinto()` (binary I/O).
      • Splits each chunk on b"\n" and uses a `remainder` buffer to carry partial lines
        across chunk boundaries.
      • Decodes each complete line to text and prints it. Emits any final unterminated
        line at EOF.

    Key Concepts
    ------------
    • bytearray:
        A mutable sequence of bytes, useful as a reusable I/O buffer because functions
        like `f.readinto()` can write directly into its memory (avoids creating a new
        bytes object for each read).

    • `(n := f.readinto(buffer))` and `chunk = buffer[:n]`:
        `readinto(buffer)` fills up to `len(buffer)` bytes and returns the actual count `n`.
        Only the first `n` bytes are valid; `buffer[:n]` slices those bytes for processing.
        (Note: `buffer[:n]` produces a *copy*; for zero-copy, use `memoryview(buffer)[:n]`.)

    • While + For loop:
        The outer `while` reads fixed-size chunks until EOF (`n == 0`). The inner loop
        splits the current chunk on b"\n". All complete lines are emitted; the last
        element (potentially incomplete) is saved in `remainder` to be prefixed to the
        next chunk.

    Newline & EOF Handling
    ----------------------
    • Lines are separated on LF (b"\n"). This function does not strip CR (b"\r"); on
      Windows CRLF files you may see a trailing "\r". Trim if needed before decode.
    • At EOF, if `remainder` is non-empty, it is decoded and emitted as the final line.

    Performance & Caveats
    ---------------------
    • `remainder + chunk` creates a new bytes object each iteration. For large files,
      prefer a `bytearray` accumulator with `.extend()` to avoid repeated allocations.
    • `buffer[:n]` copies; consider `memoryview` for zero-copy access.
    • The current buffer size (20) is intentionally tiny for demonstration; use a larger
      size (e.g., 64 KiB) for throughput.
    • Decoding uses the default system encoding via `.decode()`. Specify encoding and
      error handling if your input may contain non-UTF-8 bytes.

    """
    # manual buffer management
    # buffer = bytearray(4096)  # creates a reusable 4 KB block of memory for reading chunks of the file.
    buffer = bytearray(20)  # https://docs.python.org/3/library/stdtypes.html#bytearray-objects
    try:
        # Read file line by line
        with open(file=fpath, mode="rb") as f:
            remainder = b""  # Temporary buffer to hold partial lines
            # Python’s walrus operator (:=) allows you to assign values to variables as part of an expression.
            # https://realpython.com/python-walrus-operator/
            while (n := f.readinto(buffer)) > 0:  # The `f.readinto()` method is available only for binary objects
                chunk = buffer[:n]
                temp_buffer = remainder + chunk
                lines = temp_buffer.split(b"\n")
                # The last element is a partial line or empty
                remainder = lines.pop(-1)
                if lines:
                    for line in lines:
                        print("read:", line.decode())

            # print the final line, if present
            if remainder:
                print("read:", remainder.decode().strip())
    except FileNotFoundError:
        logger.error("File Not Found at path: {}".format(fpath))
    except Exception as e:
        logger.exception(e)


def read_file_with_manual_buffer_v2(fpath: str) -> None:
    """
    Read a file line-by-line using low-level, manual buffering.

    Concepts:
    - Preallocates a mutable `bytearray` and fills it with `readinto()` (no per-chunk allocations).
    - Accumulates bytes in `pending` until a newline is found; handles lines spanning chunks.
    - Strips optional CR for Windows CRLF; decodes each complete line with configurable encoding.
    - Uses `buffering=0` to avoid double-buffering since we manage buffering ourselves.
    """
    # manual buffer management
    buffer = bytearray(20)  # https://docs.python.org/3/library/stdtypes.html#bytearray-objects
    try:
        # Read file line by line
        # Since we are doing our own buffering, open with buffering=0 in binary mode
        with open(file=fpath, mode="rb", buffering=0) as f:
            pending = bytearray()
            while (n := f.readinto(buffer)) > 0:
                # chunk = buffer[:n]    # Creates a copy in the memrory

                # ref: https://docs.python.org/3/c-api/memoryview.html
                # A `memoryview` is a built-in object that provides a way to access the internal data buffer
                # of an object without creating a copy of that data.
                chunk = memoryview(buffer)[:n]  # zero-copy view of valid bytes
                pending.extend(chunk)  # appends the memory chunk to our accumulator
                # temp_buffer = remainder + chunk allocates a new bytes object every iteration
                # (can go O(n²) on big files). Prefer a bytearray accumulator and .extend() to mutate in place.

                # Extract Complete lines
                while True:
                    nl = pending.find(b"\n")  # new-line
                    if nl == -1:
                        break

                    line_bytes = pending[:nl]
                    # Drop CR for CRLF
                    # With Windows CRLF, will print stray \r characters. Strip them before decode
                    if line_bytes.endswith(b"\r"):
                        line_bytes = line_bytes[:-1]

                    print("read:", line_bytes.decode())

                    # Remove emitted line + newline from pending
                    del pending[: nl + 1]

            if pending:
                if pending.endswith(b"\r"):
                    pending = pending[:-1]
                print("read:", pending.decode())
                del pending

    except FileNotFoundError:
        logger.error("File Not Found at path: {}".format(fpath))
    except Exception as e:
        logger.exception(e)


def read_lines_os_fd_v1(fpath: str) -> None:
    r"""
    Read a text file line by line using raw OS syscalls via `os.open`/`os.read`.

    What this does
    --------------
    - Opens the file with `os.open(..., os.O_RDONLY)` to obtain a POSIX file descriptor (fd),
      bypassing Python's higher-level file object and buffering.
    - Repeatedly calls `os.read(fd, 1024)` to pull fixed-size binary chunks directly from the OS.
    - Accumulates chunks into an in-memory byte buffer and splits on the newline byte (b"\n").
    - Emits complete lines as soon as they're available; after EOF, emits any remaining bytes
      as the final line (even if it lacks a trailing newline).

    Why it's lower-level
    --------------------
    This avoids Python's file object iteration and decoding. You manually control:
      • buffering (chunk size, accumulation),
      • line detection (b"\n"),
      • decoding (`bytes.decode()`).

    Caveats / notes
    ---------------
    - `buffer += chunk` creates a new bytes object each iteration; for large files prefer a
      `bytearray` accumulator and `.extend()` to reduce copying.
    - Only splits on LF; for CRLF files you may see trailing `\r` per line unless you strip it.
    - Decoding uses the default encoding; specify an explicit encoding/error policy if needed.
    """
    fd = None
    try:
        fd = os.open(fpath, flags=os.O_RDONLY)
        buffer = b""
        while True:
            # Read 1024 bytes at a time
            chunk = os.read(fd, 1024)
            if not chunk:
                break

            buffer += chunk
            while b"\n" in buffer:
                line, buffer = buffer.split(b"\n", 1)
                print("read:", line.decode().strip())

        # Read the last line if present
        if buffer:
            print("read:", buffer.decode())
    except FileNotFoundError:
        logger.error("File Not Found at path: {}".format(fpath))
        sys.exit(0)
    except Exception as e:
        logger.exception(e)
    finally:
        if fd:
            os.close(fd)


def read_lines_os_fd_v2(fpath: str) -> None:
    r"""
    Stream a text file line-by-line using raw OS syscalls (`os.open`/`os.read`) with low allocation overhead.

    What it does
    ------------
    - Reads fixed-size binary chunks with `os.read(fd, chunk_size)`.
    - Accumulates bytes in a `bytearray` (`pending`) and emits complete lines when `\n` appears.
    - Optionally strips trailing `\r` (CRLF) before decoding and printing.

    Why this version
    ----------------
    - Avoids `buffer += chunk` (which copies) by using `bytearray.extend()` (in-place growth).

    """
    fd = None
    try:
        fd = os.open(fpath, flags=os.O_RDONLY)
        buffer = bytearray()
        while True:
            # Read 1024 bytes at a time
            chunk = os.read(fd, 1024)
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

                print("read:", line_bytes.decode())

                # Drop emitted line + '\n' from the accumulator
                del buffer[: nl + 1]

        # Read the last line if present
        if buffer:
            if buffer.endswith((b"\r")):
                buffer = buffer[:-1]
            print("read:", buffer.decode())

    except FileNotFoundError:
        logger.error("File Not Found at path: {}".format(fpath))
        sys.exit(0)
    except Exception as e:
        logger.exception(e)
    finally:
        if fd:
            os.close(fd)


# ref:
# - https://realpython.com/python-mmap/
# - https://docs.python.org/3/library/mmap.html
def read_lines_mmap(fpath: str) -> None:
    r"""
    Read a text file line-by-line using a memory-mapped view (mmap).

    How it works
    ------------
    - Opens the file read-only and maps its entire size into virtual memory with
      `mmap.ACCESS_READ`. The OS serves file pages on demand (no per-line syscalls).
    - Iterates lines using `iter(mm.readline, b"")` until EOF. Each returned line
      ends with `b"\n"` (if present); on Windows CRLF files lines end with `b"\r\n"`.
    - Optionally strips a trailing `\r` before decoding each line.

    When to use mmap
    ----------------
    - Large files where you want minimal syscall overhead and/or random access by
      offset.
    - Scanning and parsing workflows where you might revisit regions without re-reading.

    Caveats
    -------
    - Empty files cannot be mapped (ValueError); handle size==0 first.
    - A mapping does not grow if the file is appended to (not suitable for `tail -f` style reading).
    - On 32-bit systems or extremely large files, mapping may fail due to address-space limits.
    - Decoding policy matters: pass `encoding`/`errors` explicitly.
    """
    try:
        with open(fpath, "rb") as f:
            size = os.fstat(fd=f.fileno()).st_size
            if size == 0:
                logger.info("Empty File!")
                return  # Empty files cannot be mmapped

            with mmap.mmap(fileno=f.fileno(), length=size, access=mmap.ACCESS_READ) as mm:
                for line in iter(mm.readline, b""):
                    line = line.rstrip(b"\r\n")
                    print("read:", line.decode())
    except FileNotFoundError:
        logger.error("File Not Found at path: {}".format(fpath))
        sys.exit(0)
    except Exception as e:
        logger.exception(e)


def main():
    path = os.curdir + "/messages.txt"
    # read_lines(fpath=path)
    # read_file_with_manual_buffer_v1(fpath=path)s
    # read_file_with_manual_buffer_v2(fpath=path)
    # read_lines_os_fd_v1(fpath=path)
    # read_lines_os_fd_v2(fpath=path)
    read_lines_mmap(fpath=path)


if __name__ == "__main__":
    main()
