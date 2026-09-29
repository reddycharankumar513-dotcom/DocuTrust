from pathlib import Path


def extract_pdf_pages(path: Path) -> list[dict]:
    try:
        import fitz
    except ImportError as exc:
        raise RuntimeError("PyMuPDF is required for PDF extraction") from exc

    pages: list[dict] = []
    with fitz.open(path) as document:
        for index, page in enumerate(document, start=1):
            text = page.get_text("text").strip()
            if text:
                pages.append({"page": index, "text": text})
    return pages


def chunk_pages(pages: list[dict], chunk_size: int = 1000, chunk_overlap: int = 180) -> list[dict]:
    try:
        from langchain_text_splitters import RecursiveCharacterTextSplitter
    except ImportError:
        return _fallback_chunk_pages(pages, chunk_size, chunk_overlap)

    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks: list[dict] = []
    for page in pages:
        for text in splitter.split_text(page["text"]):
            chunks.append({"page": page["page"], "text": text})
    return chunks


def _fallback_chunk_pages(pages: list[dict], chunk_size: int, chunk_overlap: int) -> list[dict]:
    chunks: list[dict] = []
    stride = max(1, chunk_size - chunk_overlap)
    for page in pages:
        text = page["text"]
        for start in range(0, len(text), stride):
            chunk = text[start : start + chunk_size].strip()
            if chunk:
                chunks.append({"page": page["page"], "text": chunk})
    return chunks
