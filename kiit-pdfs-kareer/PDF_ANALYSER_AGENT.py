import os
import torch
from transformers import AutoTokenizer, AutoModel
from agno.agent import Agent
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.models.groq import Groq
from agno.vectordb.lancedb import LanceDb, SearchType

# --- Environment Variable Check ---
# List the required environment variables.

required_env_vars = ['GROQ_API_KEY']

for var in required_env_vars:
    if not os.environ.get(var):
        raise EnvironmentError(
            f"{var} environment variable is not set. "
            f"Please set {var} before running the script."
        )

# --- Custom Embedder Definition ---
class HFEmbedder:
    def __init__(self, model_name="bert-base-uncased"):
        # Load the tokenizer and model from Hugging Face
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.model.eval()  # Set the model to evaluation mode
        # Set the dimensions attribute to the model's hidden size
        self.dimensions = self.model.config.hidden_size

    def embed(self, texts):
        """
        Compute embeddings for a given text or list of texts.
        This function performs mean pooling over the token embeddings.
        """
        # Ensure texts is a list
        if isinstance(texts, str):
            texts = [texts]
        with torch.no_grad():
            inputs = self.tokenizer(
                texts, return_tensors='pt', padding=True, truncation=True
            )
            outputs = self.model(**inputs)
            # Mean pooling over the token embeddings to obtain a single vector per text
            embeddings = outputs.last_hidden_state.mean(dim=1)
        # Return embeddings as numpy arrays
        return embeddings.numpy()

    def get_embedding(self, text):
        """
        Return the embedding for a single text.
        """
        return self.embed(text)[0]

    def get_embedding_and_usage(self, text):
        """
        Return the embedding for the text along with usage information.
        """
        embedding = self.get_embedding(text)
        usage = {}  # Optionally include details such as token count or processing time
        return embedding, usage

# --- PDF and Knowledge Base Setup ---
# Define the URL of the PDF you want to query.
pdf_url = "https://www.justice.gov/d9/criminal-ccips/legacy/2015/01/14/ccmanual_0.pdf"

# Initialize our custom HFEmbedder (using BERT)
embedder = HFEmbedder(model_name="bert-base-uncased")

# Set up LanceDb for vector storage and search.
vector_db = LanceDb(
    table_name="pdf_documents",  # Customize the table name as needed.
    search_type=SearchType.vector,
    embedder=embedder,
)

# Load the PDF into the knowledge base using PDFUrlKnowledgeBase.
knowledge_base = PDFUrlKnowledgeBase(
    urls=[pdf_url],
    vector_db=vector_db,
    embedder=embedder,
)
# Load the document into the vector DB.
# Setting 'recreate=False' avoids reprocessing if the document is already loaded.
knowledge_base.load(recreate=False)

# --- Agent Initialization ---
# Here, we pass the Groq API key via the environment variable.
pdf_qa_agent = Agent(
    name="PDFQAAgent",
    knowledge=knowledge_base,
    search_knowledge=True,
    model=Groq(id="deepseek-r1-distill-llama-70b"),  # The Groq client will automatically read the GROQ_API_KEY from the environment.
    markdown=True,
    instructions=[
        "Provide accurate and concise information based on the PDF content.",
        "Include relevant citations and references from the document when possible.",
        "Clarify that the information is based solely on the provided PDF content.",
        "Encourage further review of the document for more detailed understanding.",
    ],
)

# --- Query Execution ---
# Perform a question–answer interaction.
pdf_qa_agent.print_response(
    "What are the key legal takeaways regarding email spoofing as described in this document?",
    stream=True,  # Streaming output provides real-time feedback.
)