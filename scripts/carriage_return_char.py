r"""
In Python, the carriage return character is represented by the escape sequence \r.

It is a special control character that, when encountered in a string or output stream, moves the
cursor to the beginning of the current line without advancing to the next line.

This behavior contrasts with the newline character (\n), which moves the cursor to the beginning of
the next line. The key distinction is that \r allows for overwriting content on the same line,
while \n creates a new line for subsequent output.

How \r works:

When \r is printed, the cursor returns to the start of the current line.
Any subsequent text printed will then overwrite the existing characters on that line from the beginning.

This can be useful for creating dynamic output where you want to update information in a single line,
such as:

- Progress indicators: Displaying a percentage or status that updates in place.
- Real-time updates: Showing changing data on a single line in the console.
"""
# Example:

import time

for i in range(1, 6):
    print(f"\rProgress: {i * 20}%", end="")
    time.sleep(0.5)
print("\nDone!")

"""
In this example, \r ensures that the "Progress" message is updated on the same line, giving the appearance of
a dynamic progress bar.

The end="" argument in print() prevents a newline from being added after each update,
allowing \r to function as intended. The final print("\nDone!") adds a newline after the loop completes.
"""
