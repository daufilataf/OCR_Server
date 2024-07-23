import os
import base64
import fitz  # Ensure this import is present
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import HighlightRequestSerializer, OcrToJsonRequestSerializer
from .ocr_utils import ocr_pdf_to_json, process_pdf
import json

def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
    print(f"Directory '{directory}' created or already exists.")

@api_view(['POST'])
def ocr_to_json_view(request):
    serializer = OcrToJsonRequestSerializer(data=request.data)
    if serializer.is_valid():
        pdf_file = request.FILES['pdf_file']
        output_dir = serializer.validated_data['output_dir']

        ensure_directory_exists(output_dir)

        # Save the uploaded file to the specified directory
        pdf_path = os.path.join(output_dir, pdf_file.name)
        with open(pdf_path, 'wb+') as destination:
            for chunk in pdf_file.chunks():
                destination.write(chunk)

        # Perform OCR on the saved PDF
        ocr_pdf_to_json(pdf_path, output_dir)

        # Read the generated JSON file
        json_filename = os.path.join(output_dir, f'{os.path.basename(pdf_path).replace(".pdf", "")}.json')
        with open(json_filename, 'r', encoding='utf-8') as json_file:
            json_data = json.load(json_file)

        # Delete the PDF file after processing
        os.remove(pdf_path)

        return Response(json_data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def highlight_view(request):
    serializer = HighlightRequestSerializer(data=request.data)
    if serializer.is_valid():
        pdf_file = request.FILES['pdf_file']
        words_to_highlight = serializer.validated_data['words_to_highlight']
        output_dir = serializer.validated_data['output_dir']
        
        ensure_directory_exists(output_dir)
        
        # Save the uploaded file to the specified directory
        pdf_path = os.path.join(output_dir, pdf_file.name)
        with open(pdf_path, 'wb+') as destination:
            for chunk in pdf_file.chunks():
                destination.write(chunk)
        
        # Process the saved PDF file to highlight words
        report_path = process_pdf(pdf_path, words_to_highlight, output_dir)
        json_data = []

        num_pages = len(fitz.open(pdf_path))
        print(f"Number of pages processed: {num_pages}")

        for page_number in range(num_pages):
            image_path = os.path.join(output_dir, f'screenshot_page_{page_number + 1}.png')
            text = ""  # Assuming text is extracted somewhere in process_pdf
            if os.path.exists(image_path):
                with open(image_path, 'rb') as image_file:
                    encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
                    print(f"Encoded image for page {page_number + 1}: {len(encoded_image)} characters")
                    
                    # Collect JSON data
                    page_data = {
                        "id": page_number + 1,
                        "pdf_name": os.path.basename(pdf_path).replace('.pdf', ''),
                        "page": page_number + 1,
                        "text": text,
                        "code": encoded_image
                    }
                    json_data.append(page_data)

        report_data = None
        if os.path.exists(report_path):
            with open(report_path, 'r', encoding='utf-8') as report_file:
                report_data = report_file.read()

        print(f"Number of highlighted images: {len(json_data)}")
        print(f"Report data: {report_data}")

        response_data = {
            "pages": json_data,
            "report": report_data
        }

        # Delete the PDF file after processing
        os.remove(pdf_path)

        return Response(response_data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
