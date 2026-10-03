from document_store import (
    save_document,
    get_document,
    document_loaded
)


def save_uploaded_document(
    pdf_name,
    chunks,
    vectorstore,
    embedding_model,
    rag_chain,
    num_pages,
    extracted_characters,
    embedding_shape,
):
    save_document(
        pdf_name,
        chunks,
        vectorstore,
        embedding_model,
        rag_chain,
        num_pages,
        extracted_characters,
        embedding_shape,
    )


def get_uploaded_document():
    return get_document()


def is_document_loaded():
    return document_loaded()