import pdfplumber 
import re

def load_pdf(path):
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

def clean_headers(text):
    #* titles/headers (e.g. "BOOK XXIII", "PENELOPE EVENTUALLY RECOGNISES HER HUSBAND") 
    #* are all-caps with no ending punctuation, so the sentence splitter can't tell where they end and glues them onto whatever text follows
    #* adding a period to fix that 

    lines = text.split("\n") # split the entire text into lines based on whitespace
    cleaned_lines = []
    for line in lines: # go through the list of lines & check conditions, if empty, UPPERCASE and NOT end with . ! ? : 
        stripped = line.strip()
        if stripped and stripped.isupper() and not stripped.endswith((".", "!", "?", ":")): 
            cleaned_lines.append(stripped + ".")
        else:
            cleaned_lines.append(line)
    return "\n".join(cleaned_lines)

def strip_footnote_nums(text):
    # footnote reference numbers are stuck directly onto a word or punctuation with no space e.g. "Strait128", "estate,96", "them.179" 
    # this translation spells out numbers as words so any digits glued straight onto text like this are footnote markers, not real numbers
    text = re.sub(r'(?<=[a-zA-Z.,;:!?])\d+', '', text)
    return text

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

    #* added later  
    txt = clean_headers(txt) 
    txt = strip_footnote_nums(txt)

    # removing footnotes which is one big block tacked on after the narration ends
    footnotes_idx = txt.rfind("FOOTNOTES:")
    if footnotes_idx != -1:
        txt = txt[:footnotes_idx]
        
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


 
