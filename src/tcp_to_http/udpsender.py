import socket
import sys

# Socket Programming:
# Socket Programming in Python (Guide): https://realpython.com/python-sockets/
# Socket Programming HOWTO: https://docs.python.org/3/howto/sockets.html    <--- This is crazy good
# socket lib docs: https://docs.python.org/3/library/socket.html
# Python Socket Programming Tutorial: https://youtu.be/3QiPPX-KeSc?si=W92KcIUbOqSChcLi


# UDP REference Links
# UDP Communication: https://wiki.python.org/moin/UdpCommunication


HOST, PORT = "127.0.0.1", 42069

client_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)


def using_while():
    """
    Interactive UDP line sender.

    Prompts with '> ' in an infinite loop, reads a line via input(),
    appends a newline, and sends it as a single UDP datagram to HOST:PORT.
    Exits cleanly on Ctrl+C or EOF. Keeps the socket connected (sets a
    default remote) so .send() can be used instead of sendto().
    """
    try:
        client_socket.connect((HOST, PORT))
        while True:
            line = input("> ")
            if not line:
                continue

            data = (line + "\n").encode("utf-8")
            # client_socket.sendto(data, (HOST, PORT))
            try:
                client_socket.send(data)
            except ConnectionRefusedError:
                print(f"Could not connect to: {HOST}:{PORT}")
    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        client_socket.close()
        print("Exit")


def main():
    r"""
    Unified UDP sender supporting both interactive TTY and piped input.

    Behavior:
    - If stdin is a TTY: show a persistent '> ' prompt, read lines as the user types.
    - If stdin is piped/redirected: stream each incoming line without prompting.
    - Ensures each transmitted datagram ends with a single '\n' (adds one if missing).
    - Uses socket.connect() to fix the remote address so .send() can be used.
    - Ignores empty lines (just re-prompts in interactive mode).
    - Gracefully handles Ctrl+C / EOF and always closes the socket.

    This mirrors the Go UDP sender pattern (DialUDP + loop + ReadString)
    for experimentation with the "fire-and-forget" nature of UDP
    (no error even if nothing is listening on the target port).
    """
    try:
        client_socket.connect((HOST, PORT))
        # If stdin is a TTY, show a prompt; otherwise just stream lines
        interactive: bool = sys.stdin.isatty()
        if interactive:
            print("Press Ctrl+D to exit!")
            print("> ", end="", flush=True)

        for line in sys.stdin:
            if not line.strip():
                if interactive:
                    print("> ", end="", flush=True)
                continue

            if not line.endswith("\n"):
                line = line + "\n"
            try:
                # client_socket.sendto(line.encode("utf-8"), (HOST, PORT))
                # ^^^socket.sendto(...) requires the host and port to passed and you do not need to
                # explicitly do `socket.connect()`.
                # ref: https://docs.python.org/3/library/socket.html#socket.socket.sendto

                client_socket.send(line.encode("utf-8"))
                # ^^^While socket.send() expects that you setup the connection prior using socket.connect()
                # and if the udp connection is not established, it raises ConnectionRefusedError
                # ref: https://docs.python.org/3/library/socket.html#socket.socket.send
            except ConnectionRefusedError:
                print(f"Could not connect to: {HOST}:{PORT}")
                break

            if interactive:
                print("> ", end="", flush=True)
        else:
            if not interactive:
                print("File sent!")

    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        client_socket.close()


if __name__ == "__main__":
    main()


"""
ref: https://docs.python.org/3/library/sys.html#sys.stdin

`sys.stdin.isatty()` in Python is a method that checks whether the standard input
stream (sys.stdin) is connected to a terminal device (also known as a TTY, or Teletypewriter).

Returns True:
    If sys.stdin is connected to an interactive terminal, meaning a user is likely
    interacting directly with the program through a command prompt or shell.

Returns False:
    If sys.stdin is not connected to a terminal, which typically means the input is being
    redirected from a file, a pipe, or another non-interactive source.


import sys

if sys.stdin.isatty():
    print("Running in an interactive terminal.")
    user_input = input("Enter something: ")
    print(f"You entered: {user_input}")
else:
    print("Running in a non-interactive environment (e.g., piped input or file redirection).")
    # Read from stdin without prompting
    content = sys.stdin.read()
    print(f"Input received:\n{content}")
"""
