# Build an API-based Generative AI application using Docker

This simple example demonstrates how to build an API-based Generative AI application using Docker.

We will build a lightweight Python FastAPI web server inside a Docker container. This server will accept a prompt from a user, securely pass it to the OpenAI API using an API key injected via environment variables, and return the AI's response.

## 1. The Application Files:
a. Create a new folder and place these three simple files inside it:

main.py (The Python Web App)

```
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI(title="Docker GenAI API Wrapper")

# Initialize the OpenAI client. It automatically looks for the OPENAI_API_KEY env variable.
if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("OPENAI_API_KEY environment variable is missing!")

client = OpenAI()

class AIQuery(BaseModel):
    prompt: str

@app.post("/ask")
async def ask_ai(query: AIQuery):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Using a fast, lightweight model
            messages=[{"role": "user", "content": query.prompt}]
        )
        return {"reply": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```


b. Create a requirements.txt with the following dependencies:
```
Plaintext
fastapi
uvicorn
openai
pydantic
```

c. Create the following Dockerfile
```
# Step 1: Use a slim Python base image
FROM python:3.11-slim

# Step 2: Set the working directory inside the container
WORKDIR /app

# Step 3: Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Step 4: Copy the application code
COPY main.py .

# Step 5: Expose the port FastAPI will run on
EXPOSE 8000

# Step 6: Start the Uvicorn web server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```



## 2. How to Build and Run Your GenAI Container:
Open your terminal inside the folder containing these files and execute the following commands:

Step A: Build the Docker Image
Wrap your Python app and its dependencies into an image named genai-api-app.

docker build -t genai-api-app .


Step B: Run the Container (Injecting your API Key)
When you run the container, use the -e flag to securely pass your actual OpenAI API key into the container environment without hardcoding it into your code.

docker run -d -p 8000:8000 -e OPENAI_API_KEY="your_actual_openai_api_key_here" --name my-ai-app genai-api-app


## 3. How to Test Your App:
Your containerized AI application is now listening on port 8000. You can test it by sending a POST request using curl from your terminal:

curl -X POST "http://localhost:8000/ask" \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Give me a 3-word slogan for Docker."}'


Expected Response:

JSON
{"reply": "Pack. Ship. Run."}



## Why Docker Matters for this Setup
Security (Secret Handling): By utilizing Docker's environment variable injection (-e), you keep your sensitive cloud API keys completely out of your Git source control and your base image.

Zero Setup Dependency: Anyone else on your team can download this exact image and run it instantly. They do not need to install Python, FastAPI, or manage version mismatches with the OpenAI SDK on their local machine.
