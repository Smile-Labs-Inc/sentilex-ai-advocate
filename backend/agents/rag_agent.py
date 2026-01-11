
import os
from langchain_pinecone import PineconeVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Singleton instance for the vector store
_vector_store_instance = None

def get_vector_store():
    """
    Returns the singleton instance of the PineconeVectorStore.
    Initializes it only if it hasn't been created yet.
    """
    global _vector_store_instance
    
    if _vector_store_instance is not None:
        return _vector_store_instance

    print("Initializing Pinecone Vector Store...")
    
    idx_name = os.environ.get("PINECONE_INDEX_NAME", "law-index")
    
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    _vector_store_instance = PineconeVectorStore.from_existing_index(
        index_name=idx_name,
        embedding=embeddings
    )
    
    return _vector_store_instance

def get_law_rag_chain():
    """
    Creates and returns the RAG chain for legal queries.
    """
    vectorstore = get_vector_store()
    retriever = vectorstore.as_retriever()
    
    template = """You are a specialized legal AI assistant for Sri Lankan Law.
    Answer the question based ONLY on the following context.
    If the context does not contain the answer, say "I cannot find the answer in the provided legal documents."
    
    Cite the relevant sections or acts from the context in your answer.
    
    Context:
    {context}
    
    Question: {question}
    """
    
    prompt = ChatPromptTemplate.from_template(template)
    model = ChatGoogleGenerativeAI(model="gemini-pro")
    
    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | model
        | StrOutputParser()
    )
    
    return chain
