import json
import base64
import os

def decode_base64_images(json_file, output_dir):
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Read the JSON file
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for page_data in data:
        page_id = page_data['id']
        encoded_image = page_data['screenshot']
        
        # Decode the base64-encoded image
        image_data = base64.b64decode(encoded_image)
        
        # Save the image as a file
        image_filename = os.path.join(output_dir, f'page_{page_id}.png')
        with open(image_filename, 'wb') as image_file:
            image_file.write(image_data)
        
        print(f"Decoded and saved image for page {page_id} to {image_filename}")

# Example usage
json_file = 'output_directory2/test3_highlighted.json'
output_dir = 'decoded_images'

decode_base64_images(json_file, output_dir)
