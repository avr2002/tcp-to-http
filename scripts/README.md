Archive of Scripts:
======================

1. [read_bytes.py](./read_bytes.py)
   - Read a file in binary mode, using `os.open()` and `os.read()` and print it's contents 8 bytes at a time.
2. [read_lines.py](./read_lines.py)
   - Read a file line by line, using various techniques:
        1. Using standard Python's built-in `open()` method.
        2. Using manual buffering, `bytearray` and `readinto()`.
        3. Using manual buffering and `memoryview()` for zero-copy reads.
        4. Using `mmap` for memory-mapped file I/O.