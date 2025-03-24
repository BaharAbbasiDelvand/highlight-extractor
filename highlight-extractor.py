import fitz  # pymupdf
import re
import sys
import os

def extract_pdf_highlights(pdf_path):
    doc = fitz.open(pdf_path)
    entries = []

    for page_num, page in enumerate(doc):
        # grab all the text so i can search sentences properly
        page_text = page.get_text()
        sentences = re.split(r'(?<=[.!?]) +', page_text)

        # collect all highlighted words on this page
        highlighted_words = []
        annot = page.first_annot
        while annot:
            if annot.type[0] == 8:  # highlight
                word = ""
                quad_points = annot.vertices
                for i in range(0, len(quad_points), 4):
                    rect = fitz.Quad(quad_points[i:i+4]).rect
                    word += page.get_textbox(rect) + " "
                highlighted_words.append(word.strip())
            annot = annot.next

        # now loop through sentences and check if any highlighted word is inside
        for sent in sentences:
            added = False
            for word in highlighted_words:
                if word and word in sent:
                    # underline the word in the sentence with <u></u>
                    underlined_sent = sent.replace(word, f"<u>{word}</u>")
                    entries.append((underlined_sent, page_num + 1))
                    added = True
                    break  # stop after first match to avoid duplicates
            if added:
                continue

    doc.close()

    # auto-generate the output filename
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    output_md = f"{base_name}-highlightednotes.md"

    # write everything to markdown
    with open(output_md, 'w', encoding='utf-8') as md:
        md.write("# highlighted context from pdf\n\n")
        for sentence, page in entries:
            md.write(f"- (page {page}) {sentence}\n")

    print(f"✅ highlights saved to: {output_md}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: python extract_highlights.py input.pdf")
        sys.exit(1)

    pdf_file = sys.argv[1]
    extract_pdf_highlights(pdf_file)
