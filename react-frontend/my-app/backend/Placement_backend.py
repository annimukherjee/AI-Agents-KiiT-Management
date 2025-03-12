import os
import torch
from transformers import AutoTokenizer, AutoModel
from agno.agent import Agent
from agno.knowledge.pdf import PDFKnowledgeBase, PDFReader
from agno.models.groq import Groq
from agno.vectordb.lancedb import LanceDb, SearchType
from dotenv import load_dotenv
from fastapi import APIRouter
from pydantic import BaseModel

load_dotenv()

router = APIRouter(
    prefix="/placement",  # Adds this prefix to all routes
    tags=["placement"],   # For API documentation grouping
)

# --- Environment Variable Check ---
required_env_vars = ['GROQ_API_KEY']
for var in required_env_vars:
    if not os.environ.get(var):
        raise EnvironmentError(f"{var} environment variable is not set. Please set {var} before running the script.")

# --- Custom Embedder Definition ---
class HFEmbedder:
    def __init__(self, model_name="bert-base-uncased"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.model.eval()
        self.dimensions = self.model.config.hidden_size

    def embed(self, texts):
        if isinstance(texts, str):
            texts = [texts]
        with torch.no_grad():
            inputs = self.tokenizer(texts, return_tensors='pt', padding=True, truncation=True)
            outputs = self.model(**inputs)
            embeddings = outputs.last_hidden_state.mean(dim=1)
        return embeddings.numpy()

    def get_embedding(self, text):
        return self.embed(text)[0]

    def get_embedding_and_usage(self, text):
        embedding = self.get_embedding(text)
        usage = {}  # Can include token count or processing time if needed
        return embedding, usage

# --- Local PDF Setup ---
pdf_directory = r"C:\Users\AmanDeep\OneDrive\Desktop\AI-Agents-KiiT-Management\-placement-agent\kiit-pdfs-kareer"

embedder = HFEmbedder(model_name="bert-base-uncased")

vector_db = LanceDb(
    table_name="college_placement_docs",
    search_type=SearchType.vector,
    embedder=embedder,
)

knowledge_base = PDFKnowledgeBase(
    path=pdf_directory,
    vector_db=vector_db,
    reader=PDFReader(chunk=True)
)

knowledge_base.load(recreate=False)

# --- Agent Initialization ---
pdf_qa_agent = Agent(
    name="PlacementQAAgent",
    knowledge=knowledge_base,
    search_knowledge=True,
    model=Groq(id="deepseek-r1-distill-llama-70b"),
    markdown=True,
    instructions=[
        "Provide accurate and concise information based on the uploaded placement PDFs.",
        "If a user asks about applying to an internship, retrieve the application link and eligibility criteria from the PDFs.",
        "Clearly highlight important details such as deadlines, required qualifications, and the application process.",
        "Encourage the user to review the full details in the document if needed.",
        "Remember previous queries in this session and provide responses based on context.",
    ],
)

# --- Chat Memory for Context Retention ---
chat_history = []

def ask_agent(user_query):
    global chat_history

    # Append user's question to history
    chat_history.append({"role": "user", "content": user_query})

    # Convert chat history into a single string
    conversation_context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in chat_history])

    # Generate the response using the agent's run method
    response = pdf_qa_agent.run(conversation_context).content

    # Append AI response to history
    chat_history.append({"role": "assistant", "content": response})

    return response

# --- API Endpoint for Chatbot --- 
class BotRequest(BaseModel):
    message: str

@router.post("/bot")
async def get_bot_response(request: BotRequest):
    user_message = request.message
    response_text = ask_agent(user_message)
    return {"response": response_text}
