import flask
import tp4

from tp4 import app

print("\033[96m" + """
[INFO]   This is my version of TP4.
[INFO]   Disclaimer: there are multiple valid ways to achieve the same objective; this implementation shows one possible approach.
[INFO]   Docstrings have been added to all functions (generated with ChatGPT) to improve code readability and understanding.
[INFO]   If you have any questions, feel free to ask!
[INFO]   Lorcan :)
    """ + "\033[0m")
app.run(debug=True)

