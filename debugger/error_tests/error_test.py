# Missing docstring
def calculate_sum(a, b):
    return a + b

# Unused import
import datetime

# Undefined variable
def process_data():
    print(undefined_variable)

# Syntax error in function
def bad_function():
    print("This is wrong")

# Inconsistent indentation
def messy_function():
    print("Wrong indentation")
    print("This is also wrong")

def unused_vars():
    x = 10
    y = 20
    return x

# Too many arguments
def too_many_args(a, b, c, d, e, f, g, h, i, j, k):
    return a + b

# Line too long
very_long_line = "This is a very long line that exceeds the recommended maximum length of 79 characters and should be flagged by the linter"

# Multiple statements on one line
x = 1
y = 2
print(x + y)

# Bad variable name
def bad_naming():
    a = 1
    b = 2
    return a + b 