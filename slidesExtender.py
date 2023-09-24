from PyPDF2 import PdfReader, PdfWriter, Transformation
from reportlab.pdfgen import canvas
import os
import re


def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    return [atoi(c) for c in re.split("(\d+)", text)]


# Create a blank PDF with the title at the top
def create_blank_pdf(file_name, title, width, height):
    c = canvas.Canvas(file_name, pagesize=(float(width), float(height)))
    c.drawString(100, float(height) - 50, title)
    c.save()


# Extend the width of an existing PDF page
def extend_page_width(original_page, blank_pdf_name):
    width = original_page.mediabox.width
    height = original_page.mediabox.height
    # Double the width but keep the height the same
    create_blank_pdf(blank_pdf_name, "", 2 * width, height)
    extended_page = PdfReader(blank_pdf_name).pages[0]
    extended_page.add_transformation(Transformation().translate(0, 0))
    extended_page.merge_page(original_page)
    os.remove(blank_pdf_name)  # Clean up by deleting the temp file
    return extended_page


# Add a title page and append other pages
def append_pdf_with_title(input_pdf, output_pdf_writer, title):
    reader = PdfReader(input_pdf)
    num_pages = len(reader.pages)
    # Check for empty or corrupted files
    if num_pages == 0:
        print(f"Skipped empty or corrupted file: {input_pdf}")
        return

    first_page = reader.pages[0]
    width = first_page.mediabox.width
    height = first_page.mediabox.height
    title_pdf_name = "title_temp.pdf"
    create_blank_pdf(title_pdf_name, title, width, height)

    title_pdf = PdfReader(title_pdf_name)
    title_page = title_pdf.pages[0]
    output_pdf_writer.add_page(title_page)
    os.remove(title_pdf_name)  # Clean up the temp file

    for i in range(num_pages):
        original_page = reader.pages[i]
        blank_pdf_name = "blank_temp.pdf"
        extended_page = extend_page_width(original_page, blank_pdf_name)
        output_pdf_writer.add_page(extended_page)


# Entry point of the program
def main():
    folder_path = input("Inserisci il percorso della cartella contenente i PDF: ")
    output_filename = input("Inserisci il nome del file PDF risultante: ")
    output_pdf_writer = PdfWriter()

    # Ottieni tutti i file PDF dalla directory e ordinali naturalmente
    all_files = [file_name for file_name in os.listdir(folder_path) if file_name.endswith('.pdf')]
    sorted_files = sorted(all_files, key=natural_keys)

    # Loop through the PDFs in the given folder
    for file_name in sorted_files:
        if file_name.endswith(".pdf"):
            full_path = os.path.join(folder_path, file_name)
            title = file_name[:-4]  # Remove '.pdf' to get the title
            append_pdf_with_title(full_path, output_pdf_writer, title)

    # Write all the collected pages to the output PDF
    with open(output_filename, "wb") as output_pdf_file:
        output_pdf_writer.write(output_pdf_file)

    print(f"PDF combinato salvato come {output_filename}")


if __name__ == "__main__":
    main()
