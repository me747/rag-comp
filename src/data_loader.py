import pdfplumber 

def load_pdf(path):
    # could also try PyPDF2 i think, but pdfplumber seems to be better overall

    plain_text = ""
    
    with pdfplumber.open(path) as pdf:
        print(f"Opening {path}, it has {len(pdf.pages)} pages\n")

        for i, page in enumerate(pdf.pages):
            page_text = page.extract_text()

            if page_text is None:
                print(f"page {i} came back empty, skipping it")
                continue

            plain_text += page_text + "\n"

    return plain_text

def load_txt(txt_path):
    with open(txt_path, "r", encoding="utf-8") as f:
        raw_txt = f.read()
    
    # gutenberg books seem to have a licensed header/footer, i only need what's between them
    start_marker = "*** START OF THE PROJECT GUTENBERG EBOOK THE ODYSSEY ***"
    end_marker = "*** END OF THE PROJECT GUTENBERG EBOOK THE ODYSSEY ***"

    start_idx = raw_txt.find(start_marker)
    start_idx = raw_txt.find("\n", start_idx) + 1 # after finding start idx, moving idx past the marker line
    end_idx = raw_txt.find(end_marker)

    txt = raw_txt[start_idx:end_idx]

    return txt.strip()

# quick test to check if the extracted text has any formatting or visual bugs
if __name__ == '__main__':
    text = load_pdf("data/10050-medicare-and-you.pdf")

    print("*****First 500 characters*****")
    print(text[:500])
    print("*****End Preview*****")

    print(f"total length {len(text)} characters")


    od_text = load_txt("data/the_odyssey.txt")

    print("*****First 500 characters*****")
    print(od_text[:500])
    print("*****End Preview*****")

    print(f"total length {len(od_text)} characters")


 
