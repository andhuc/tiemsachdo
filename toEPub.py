import re
import fitz
from ebooklib import epub
import os
import uuid

skip_keywords = ["Ebook miễn phí tại : www.Sachvui.Com"]


def pdf_to_epub(pdf_path):
    doc = fitz.open(pdf_path)
    book = epub.EpubBook()

    book.set_identifier(str(uuid.uuid4()))
    book.set_title(os.path.basename(pdf_path))
    book.set_language("en")

    chapters = []
    img_count = 0
    img_added = 0

    for i, page in enumerate(doc):
        text = page.get_text("text").strip()
        images_html = ""

        images = page.get_images(full=True)
        img_count += len(images)

        if text.strip() == "" and len(images) == 1 and (i == 0 or i == len(doc) - 1):
            continue

        for keyword in skip_keywords:
            text = re.sub(rf"\b{re.escape(keyword)}\b", "", text, flags=re.IGNORECASE)

        for img in images:
            xref = img[0]
            base_image = doc.extract_image(xref)
            img_bytes = base_image["image"]
            img_ext = base_image["ext"]
            img_name = f"image_{i}_{img_added}.{img_ext}"
            img_added += 1

            epub_img = epub.EpubItem(
                uid=img_name,
                file_name=img_name,
                media_type=f"image/{img_ext}",
                content=img_bytes,
            )
            book.add_item(epub_img)

            images_html += f'<img src="{img_name}" alt="{img_name}" />'

        content = f"<p>{text.replace(chr(10), '<br/>')}</p>{images_html}"
        c = epub.EpubHtml(file_name=f"page_{i+1}.xhtml", lang="en")
        c.content = content
        book.add_item(c)
        chapters.append(c)

    book.toc = chapters
    book.spine = chapters  # no nav

    base_name = os.path.splitext(pdf_path)[0]
    epub_path = base_name + ".epub"
    epub.write_epub(epub_path, book)
    print(f"EPUB saved to: {epub_path}")
    print(f"Image count: {img_count}")
    print(f"Images added: {img_added}")


# Prompt user for input
pdf_file = input("Enter PDF filename (with .pdf): ")
if not os.path.exists(pdf_file):
    print("File not found.")
else:
    pdf_to_epub(pdf_file)
