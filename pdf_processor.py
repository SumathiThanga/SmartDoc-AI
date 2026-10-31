import pymupdf
from pathlib import Path

docfolder = Path("Documents")

def extract_all_pdfs(folder):
    all_pages = []
    pdf_files = list(folder.glob("*.pdf"))
    for pdf_path in pdf_files:
        print(f"\nprocessing pdf {pdf_path}")
        document = pymupdf.open(pdf_path)
        for page_number,page in enumerate(document):
            text = page.get_text()
            if text.strip:
                all_pages.append({"document_name":pdf_path.name,"page_number":page_number + 1,"text":text})


        document.close()
    return all_pages    


def create_chunks(pages, chunk_size=700, overlap=100):
    chunks = []
    for page in pages:
        text = page["text"]
        start = 0
        while(start<len(text)):
            end = start + chunk_size
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append({"document_name":page["document_name"],
                               "page_number":page["page_number"],
                               "chunk_id":len(chunks),
                               "text":chunk_text
                               })   
            start += chunk_size - overlap
    return chunks
if __name__ == "__main__":

    pages = extract_all_pdfs(docfolder)  
    print("\n total extracted pages",len(pages))
    chunks = create_chunks(pages)
    print("\n total chunks",len(chunks))
    for chunk in chunks[:10]:

        print("\n----------------------------")

        print("Document:", chunk["document_name"])

        print("Page:", chunk["page_number"])

        print("Chunk ID:", chunk["chunk_id"])

        print("Text:", chunk["text"][:250]) 
                   
