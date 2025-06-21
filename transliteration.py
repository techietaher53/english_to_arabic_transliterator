from langchain_community.document_loaders import CSVLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain.llms import HuggingFaceHub
from dotenv import load_dotenv
import os
from langchain_huggingface import HuggingFacePipeline
from transformers import pipeline ,AutoModelForCausalLM, AutoTokenizer

# Load your Hugging Face token from .env file
load_dotenv()
HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")
print("Loaded token:", HUGGINGFACEHUB_API_TOKEN)

# Step 1: Load your transliteration dataset
file_path = "transliteration_dataset.csv"
if not os.path.exists(file_path):
    raise FileNotFoundError(f"{file_path} does not exist.")

loader = CSVLoader(file_path=file_path)
documents = loader.load()
print(len(documents))


# Step 2: Create embeddings using HuggingFace
embedding = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Step 3: Store the vector embeddings in Chroma
vectordb = Chroma.from_documents(documents, embedding)

# Step 4: Choose a supported text generation model
model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")
tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")

pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=10,
        temperature=0.5,
        
    )

llm = HuggingFacePipeline(pipeline=pipe)

    

# Step 5: Create a QA chain
qa = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectordb.as_retriever(),
    chain_type="stuff"
)
# Step 6: Ask a question
query = "Salaam e Jameel"
try:
    result = qa.run(query)
    
    print("✅ Output:", result)
except Exception as e:
    print("\n--- ERROR OCCURRED ---")
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {e}")
    print("\n--- Troubleshooting Tips ---")
    print("1. Ensure you have the latest 'transformers' and 'accelerate' libraries: 'pip install --upgrade transformers accelerate'")
    print("2. Check your internet connection for model download.")
    print("3. Try removing 'device_map=\"auto\"' from the pipeline if running on CPU or facing GPU memory issues.")
    print("4. Clear your Hugging Face cache (delete contents of ~/.cache/huggingface/hub).")
