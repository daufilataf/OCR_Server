import fitz  # PyMuPDF
import pytesseract
from pdf2image import convert_from_path
from PIL import Image, ImageDraw
import json
import os

def ocr_pdf_to_json(pdf_path, output_dir):
    print(f"Starting OCR processing for PDF: {pdf_path}")
    pdf_document = fitz.open(pdf_path)
    pdf_name = os.path.basename(pdf_path).replace('.pdf', '')
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    data = []

    for page_number in range(len(pdf_document)):
        print(f"Processing page {page_number + 1} of {len(pdf_document)}")
        page = pdf_document.load_page(page_number)
        image = convert_from_path(pdf_path, first_page=page_number + 1, last_page=page_number + 1)[0]
        
        text = pytesseract.image_to_string(image, lang='aze')
        
        page_data = {
            "pdf_name": pdf_name,
            "page": page_number + 1,
            "text": text
        }

        data.append(page_data)
    
    json_filename = f'{pdf_name}.json'
    output_json = os.path.join(output_dir, json_filename)
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"OCR processing complete. JSON output saved to: {output_json}")

def highlight_words(image_path, words, output_path, word_counts, lang='aze'):
    print(f"Highlighting words in image: {image_path}")
    image = Image.open(image_path)
    words_lower = [word.lower() for word in words]
    
    data = pytesseract.image_to_data(image, lang=lang, output_type=pytesseract.Output.DICT)
    
    overlay = Image.new('RGBA', image.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)

    found_keywords = set()  # Use a set to store unique keywords

    for i in range(len(data['text'])):
        detected_word = data['text'][i].lower()
        for word in words_lower:
            if word in detected_word:
                found_keywords.add(word)  # Add keyword to set
                x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                draw.rectangle([x, y, x + w, y + h], fill=(255, 255, 0, 128))
                draw.rectangle([x, y, x + w, y + h], outline="red", width=2)
                word_counts[word] += 1

    if found_keywords:
        image = Image.alpha_composite(image.convert('RGBA'), overlay)
        highlighted_image = image.convert('RGB')
        highlighted_image.save(output_path)
        print(f"Highlighted image saved to: {output_path}")
        return list(found_keywords)  # Convert set to list
    else:
        print(f"No keywords found in image: {image_path}")
        return []

def process_pdf(pdf_path, words_to_highlight, output_dir):
    print(f"Starting PDF processing: {pdf_path}")
    pdf_document = fitz.open(pdf_path)
    pdf_name = os.path.basename(pdf_path).replace('.pdf', '')

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    word_counts = {word.lower(): 0 for word in words_to_highlight}
    data = []
    pages_with_highlights = 0

    for page_number in range(len(pdf_document)):
        print(f"Processing page {page_number + 1} of {len(pdf_document)}")
        page = pdf_document.load_page(page_number)
        image = convert_from_path(pdf_path, first_page=page_number + 1, last_page=page_number + 1)[0]

        text = pytesseract.image_to_string(image, lang='aze')

        ss_filename = f'screenshot_page_{page_number + 1}.png'
        ss_path = os.path.join(output_dir, ss_filename)

        # Save the screenshot
        image.save(ss_path)

        # Check if the image should be saved (if it contains highlighted words)
        found_keywords = highlight_words(ss_path, words_to_highlight, ss_path, word_counts)
        
        if found_keywords:
            page_data = {
                "pdf_name": pdf_name,
                "page": page_number + 1,
                "text": text,
                "screenshot": ss_path,
                "founded_keywords": found_keywords
            }
            data.append(page_data)
            pages_with_highlights += 1
        else:
            # Delete the image file if no keywords were found
            if os.path.exists(ss_path):
                os.remove(ss_path)
                print(f"Deleted screenshot with no keywords: {ss_path}")
        
    json_filename = f'{pdf_name}.json'
    output_json = os.path.join(output_dir, json_filename)
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"PDF processing complete. JSON output saved to: {output_json}")

    report_filename = f'{pdf_name}_report.txt'
    report_path = os.path.join(output_dir, report_filename)
    with open(report_path, 'w', encoding='utf-8') as report_file:
        for word, count in word_counts.items():
            report_file.write(f'Word: {word}, Count: {count}\n')
    print(f"Report generated: {report_path}")

    return report_path, pages_with_highlights
