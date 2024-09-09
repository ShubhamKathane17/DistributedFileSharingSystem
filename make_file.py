import random
import string

# Set the length of each line and the number of lines
max_line_length = 1000
num_lines = 10000

# Define a function to generate a random line
def generate_random_line():
    line_length = random.randint(10,max_line_length)
    return ''.join(random.choice(string.ascii_letters) for _ in range(line_length))

file_name = "large_file.txt"

# Write the lines to a file
with open(file_name, "w") as file:
    for i in  range(num_lines):
        file.write(generate_random_line() + "\n")

print(f"Random lines written to {file_name}")

