# main file

import streamlit as st

from utils import (
    extract_text_from_pdfs,
    get_text_chunks,
    create_vector_store,
    user_input
)

st.set_page_config(
    page_title="PDF Chat with Gemini (RAG)",
    page_icon="📄"
)

st.title("📄 PDF Chat with Gemini (RAG)")
st.write("Upload one or more PDF files.")

pdf_docs = st.file_uploader(
    "Upload PDFs",
    accept_multiple_files=True,
    type="pdf"
)

if pdf_docs:

    with st.spinner("Reading PDFs and creating embeddings..."):

        # Step 1: Extract text
        raw_text = extract_text_from_pdfs(pdf_docs)

        # Step 2: Split text into chunks
        chunks = get_text_chunks(raw_text)

        # Step 3: Create Vector Database
        vector_store = create_vector_store(chunks)
        st.session_state.vector_store = vector_store

    st.success("✅ Knowledge Base Created Successfully!")

    st.write(f"**Characters Extracted:** {len(raw_text)}")
    st.write(f"**Number of Chunks:** {len(chunks)}")

    if chunks:

        st.subheader("First Chunk Preview")

        st.text_area(
            "Chunk",
            chunks[0],
            height=250
        )

st.divider()

st.header("Ask Questions")

question = st.text_input(
    "Ask anything about your PDF"
)

if question:

    if "vector_store" not in st.session_state:

        st.error("⚠️ Please upload a PDF first.")

    else:

        with st.spinner("Thinking..."):

            answer = user_input(
                question,
                st.session_state.vector_store
            )

        st.subheader("Answer")

        st.write(answer)