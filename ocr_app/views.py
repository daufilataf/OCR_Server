import os
import base64
import fitz  # Ensure this import is present
import hashlib
from datetime import datetime  # Import datetime module
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import HighlightRequestSerializer, OcrToJsonRequestSerializer
from .ocr_utils import ocr_pdf_to_json, process_pdf
from django.conf import settings
import json

DEFAULT_OUTPUT_DIR = "default_output_directory"

def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
    print(f"Directory '{directory}' created or already exists.")

def generate_md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

@api_view(['POST'])
def ocr_to_json_view(request):
    serializer = OcrToJsonRequestSerializer(data=request.data)
    if serializer.is_valid():
        pdf_file = request.FILES.get('pdf_file')
        pdf_path = serializer.validated_data.get('pdf_path')
        output_dir = serializer.validated_data.get('output_dir', DEFAULT_OUTPUT_DIR)

        ensure_directory_exists(output_dir)

        if pdf_file:
            try:
                print("Received PDF file via upload.")
                # Save the uploaded file to the specified directory
                pdf_path = os.path.join(output_dir, pdf_file.name)
                with open(pdf_path, 'wb+') as destination:
                    for chunk in pdf_file.chunks():
                        destination.write(chunk)
            except Exception as e:
                print(f"Error processing uploaded PDF file: {e}")
                pdf_file = None
        
        if not pdf_file and pdf_path and os.path.exists(pdf_path):
            print(f"Received PDF path: {pdf_path}")
        elif not pdf_file and (not pdf_path or not os.path.exists(pdf_path)):
            return Response({"error": "No valid PDF file or path provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Perform OCR on the PDF
        ocr_pdf_to_json(pdf_path, output_dir)

        # Read the generated JSON file
        json_filename = os.path.join(output_dir, f'{os.path.basename(pdf_path).replace(".pdf", "")}.json')
        with open(json_filename, 'r', encoding='utf-8') as json_file:
            json_data = json.load(json_file)

        if pdf_file:
            # Delete the PDF file after processing
            os.remove(pdf_path)

        return Response(json_data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def highlight_view(request):
    serializer = HighlightRequestSerializer(data=request.data)
    if serializer.is_valid():
        pdf_file = request.FILES.get('pdf_file')
        pdf_path = serializer.validated_data.get('pdf_path')
        words_to_highlight = serializer.validated_data['words_to_highlight']
        
        # Create a unique directory path based on today's date and the MD5 hash of the PDF name
        today_date = datetime.today().strftime('%Y-%m-%d')
        md5_hash = hashlib.md5(os.path.basename(pdf_path).encode()).hexdigest()
        media_dir = os.path.join(settings.MEDIA_ROOT, 'ocr_highlight', today_date, md5_hash)
        ensure_directory_exists(media_dir)
        
        # Process the saved PDF file to highlight words
        report_path, found_keywords = process_pdf(pdf_path, words_to_highlight, media_dir)

        # Ensure found_keywords is a set or list, even if it's empty
        if not isinstance(found_keywords, (set, list)):
            found_keywords = []

        response_data = []

        num_pages = len(fitz.open(pdf_path))
        print(f"Number of pages processed: {num_pages}")

        for page_number in range(num_pages):
            image_path = os.path.join(media_dir, f'screenshot_page_{page_number + 1}.png')
            if os.path.exists(image_path):
                page_data = {
                    "page": page_number + 1,
                    "path": image_path,
                    "founded_keywords": list(found_keywords),
                }
                response_data.append(page_data)

        return Response(response_data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)