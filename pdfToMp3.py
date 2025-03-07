import os
import glob
import logging
from concurrent.futures import ThreadPoolExecutor
from pypdf import PdfReader
from gtts import gTTS
from langdetect import detect

logging.getLogger("pypdf").setLevel(logging.ERROR)


def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = "\n".join(
        page.extract_text() for page in reader.pages if page.extract_text()
    )
    return text.strip()


def convert_text_to_mp3(text, lang, output_path):
    if not text:
        print(f"Skipping {output_path}: No text found.")
        return

    try:
        tts = gTTS(text, lang=lang)
        tts.save(output_path)
        print(f"Saved: {output_path}")
    except Exception as e:
        print(f"Error converting {output_path}: {e}")


def process_single_pdf(pdf_path, output_dir):
    print(f"Processing: {pdf_path}")

    text = extract_text_from_pdf(pdf_path)
    if not text:
        return

    try:
        lang = detect(text)
    except Exception:
        lang = "de"

    mp3_filename = os.path.splitext(os.path.basename(pdf_path))[0] + ".mp3"
    output_path = os.path.join(output_dir, mp3_filename)

    convert_text_to_mp3(text, lang, output_path)


def process_pdfs_in_directory(input_dir, output_dir, max_workers=4):
    os.makedirs(output_dir, exist_ok=True)

    pdf_files = glob.glob(os.path.join(input_dir, "*.pdf"))

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        executor.map(lambda pdf: process_single_pdf(pdf, output_dir), pdf_files)


if __name__ == "__main__":
    input_directory = "data/pdfs"
    output_directory = "data/mp3s"

    process_pdfs_in_directory(input_directory, output_directory, max_workers=10)
