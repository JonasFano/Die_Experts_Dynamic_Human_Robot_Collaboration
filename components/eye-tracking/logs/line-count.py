import json

# Read the JSON file
with open("tomas-with-stress.json", "r") as file:
    data = json.load(file)

# Get the length of the JSON array
lines_count = len(data)
print(f"Number of lines in the file: {lines_count}")
