from pypdf import PdfReader

import google.generativeai as genai
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_google_genai import GoogleGenerativeAIEmbeddings
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain.prompts import PromptTemplate
# from langchain.chains.question_answering import load_qa_chain
from langchain_chroma import Chroma
from dotenv import load_dotenv
import os

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found. Please check your .env file.")

genai.configure(api_key=GOOGLE_API_KEY)

def extract_text_from_pdfs(pdf_docs):

    text = ""

    for pdf in pdf_docs:

        reader = PdfReader(pdf)

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:

                text += page_text + "\n"

    return text

def get_text_chunks(text):

    splitter = RecursiveCharacterTextSplitter(

        chunk_size=1000,

        chunk_overlap=200

    )

    chunks = splitter.split_text(text)

    return chunks

def get_embedding_model():

    embeddings = GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-001",
        google_api_key=GOOGLE_API_KEY
    )

    return embeddings

def create_vector_store(chunks):

    embeddings = get_embedding_model()

    vector_store = Chroma.from_texts(

        texts=chunks,

        embedding=embeddings,

        persist_directory="chroma_db"

    )

    return vector_store


def user_input(user_question, vector_store):

    # Retrieve the top 3 relevant chunks
    docs = vector_store.similarity_search(user_question, k=3)

    # Combine the retrieved chunks into one context string
    context = "\n\n".join([doc.page_content for doc in docs])

    # Create Gemini model
    model = genai.GenerativeModel("gemini-flash-latest")

    # Create prompt
    prompt = f"""
You are a helpful AI assistant.

Answer ONLY using the context below.

If the answer is not available in the context, reply exactly:

"The answer is not available in the uploaded PDF."

Context:
{context}

Question:
{user_question}

Answer:
"""

    # Get response from Gemini
    response = model.generate_content(prompt)

    return response.text


# def get_conversational_chain():

#     prompt_template = """
#     Answer the question using ONLY the provided context.

#     If the answer is not present in the context,
#     say

#     "The answer is not available in the uploaded PDF."

#     Context:
#     {context}

#     Question:
#     {question}

#     Answer:
#     """

#     model = ChatGoogleGenerativeAI(
#         model="gemini-2.5-flash",
#         temperature=0.3,
#         google_api_key=GOOGLE_API_KEY
#     )

#     prompt = PromptTemplate(
#         template=prompt_template,
#         input_variables=["context", "question"]
#     )

#     chain = load_qa_chain(
#         model,
#         chain_type="stuff",
#         prompt=prompt
#     )

#     return chain


# def user_input(user_question, vector_store):

#     docs = vector_store.similarity_search(
#         user_question,
#         k=3
#     )

#     chain = get_conversational_chain()

#     response = chain(
#         {
#             "input_documents": docs,
#             "question": user_question
#         },
#         return_only_outputs=True
#     )

#     return response["output_text"]