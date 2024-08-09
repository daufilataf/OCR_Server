import base64
import os

def decode_base64_file(input_file_path, output_file_path):
    try:
        # Read the input file containing the Base64 encoded data
        with open(input_file_path, 'r') as input_file:
            base64_data = input_file.read()

        # Decode the Base64 data
        decoded_data = base64.b64decode(base64_data)

        # Write the decoded data to the output file
        with open(output_file_path, 'wb') as output_file:
            output_file.write(decoded_data)

        print(f"Decoded data has been written to {output_file_path}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Specify the input and output file paths here
    input_file_path = "encoded.txt"  # Change this to your actual input file path
    output_file_path = "decoded_output"  # Change this to your desired output file path

    # Ensure the input file exists
    if not os.path.isfile(input_file_path):
        print(f"The input file '{input_file_path}' does not exist.")
        exit(1)

    decode_base64_file(input_file_path, output_file_path)
