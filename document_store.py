# =====================================================
# Shared Document Store
# Used by both Streamlit and MCP Server
# =====================================================

document_data = {
    "pdf_name": None,
    "chunks": None,
    "vectorstore": None,
    "embedding_model": None,
    "rag_chain": None,
    "num_pages": 0,
    "extracted_characters": 0,
    "embedding_shape": None,
}


# =====================================================
# Save Current Document
# =====================================================

def save_document(
    pdf_name,
    chunks,
    vectorstore,
    embedding_model,
    rag_chain,
    num_pages,
    extracted_characters,
    embedding_shape,
):
    document_data["pdf_name"] = pdf_name
    document_data["chunks"] = chunks
    document_data["vectorstore"] = vectorstore
    document_data["embedding_model"] = embedding_model
    document_data["rag_chain"] = rag_chain
    document_data["num_pages"] = num_pages
    document_data["extracted_characters"] = extracted_characters
    document_data["embedding_shape"] = embedding_shape


# =====================================================
# Get Current Document
# =====================================================

def get_document():
    return document_data


# =====================================================
# Check Document Loaded
# =====================================================

def document_loaded():
    return document_data["rag_chain"] is not None