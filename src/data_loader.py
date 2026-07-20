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

# quick test to check if the extracted text has any formatting or visual bugs
if __name__ == '__main__':
    text = load_pdf("data/10050-medicare-and-you.pdf")

    print("*****First 500 characters*****")
    print(text[:500])
    print("*****End Preview*****")

    print(f"total length {len(text)} characters")


 
