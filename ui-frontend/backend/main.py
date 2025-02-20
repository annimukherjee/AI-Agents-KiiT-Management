import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your Next.js URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get user input when starting the script
user_name = input("Enter your name: ")

@app.get("/get-name")
def get_name():
    return {"name": user_name}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)