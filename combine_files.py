import os
import sys


def main():
    # Ensure that the correct number of arguments have been provided
    if len(sys.argv) != 3:
        print("Usage: python combine_files.py <input_folder> <output_file>")
        sys.exit(1)

    input_folder = sys.argv[1]
    output_file = sys.argv[2]

    # Check if the input folder exists and is indeed a directory
    if not os.path.isdir(input_folder):
        print(f"Error: {input_folder} is not a valid directory.")
        sys.exit(1)

    # Retrieve all items in the directory and filter by allowed extensions
    allowed_extensions = {".txt", ".json"}
    files = [
        f
        for f in os.listdir(input_folder)
        if os.path.isfile(os.path.join(input_folder, f))
        and os.path.splitext(f)[1].lower() in allowed_extensions
    ]

    # Sort the files for a consistent order
    files.sort()

    # Open the output file and write the combined content
    with open(output_file, "w", encoding="utf-8") as outfile:
        for f in files:
            file_path = os.path.join(input_folder, f)
            with open(file_path, "r", encoding="utf-8") as infile:
                outfile.write(infile.read())
                outfile.write("\n")  # Add a newline after each file's content

    print(
        f"All .txt and .json files from {input_folder} have been combined into {output_file}"
    )


if __name__ == "__main__":
    main()
