# Here were are going to use Hugging Face from Docker

When dockerizing Hugging Face models, the biggest hurdle developers face is image size and cold-start times. If you don't build your image carefully, Docker will download multi-gigabyte models from the cloud every single time the container spins up, leading to incredibly slow restarts.

This is an introductory example of a Sentiment Analysis API. It uses a lightweight, optimized Dockerfile layout that downloads and caches a model from the Hugging Face Hub during the build phase so it's instantly ready to run offline.

## 1. The Application Files:
### a. Create a new folder and place these three simple files inside it:

main.py (The Python Web App)

```
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import pipeline

app = FastAPI(title="Hugging Face Docker API")

# Load the pipeline. Since we pre-downloaded the weights into the image,
# this step will fetch them instantly from the local cache directory.
try:
    print("Loading sentiment analysis model from local cache...")
    classifier = pipeline(
        "sentiment-analysis", 
        model="distilbert-base-uncased-finetuned-sst-2-english"
    )
    print("Model loaded successfully!")
except Exception as e:
    print(f"Error loading model: {e}")
    classifier = None

class TextPayload(BaseModel):
    text: str

@app.post("/predict")
def predict_sentiment(payload: TextPayload):
    if not classifier:
        raise HTTPException(status_code=500, detail="Model is not initialized.")
    
    try:
        result = classifier(payload.text)[0]
        return {
            "text": payload.text,
            "sentiment": result["label"],
            "confidence": round(result["score"], 4)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))```
```

### b. Create a ```requirements.txt``` with the following dependencies:
```
fastapi==0.110.0
uvicorn==0.28.0
transformers==4.38.0
torch==2.2.1 --index-url https://download.pytorch.org/whl/cpu
pydantic==2.6.4
```

Optimization Tip: Appending ```--index-url https://download.pytorch.org/whl/cpu``` forces pip to install the CPU-only version of PyTorch. Standard PyTorch ships with massive NVIDIA CUDA binaries that push your image size past 6GB. Using the CPU variant keeps your image highly optimized and lightweight.

### c. Create the following Dockerfile
```
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies needed for compiling certain tokenizers
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- CRITICAL HUGGING FACE CACHE STEP ---
# Set the environment variable telling Hugging Face where to save models permanently
ENV HF_HOME=/app/hf_cache

# Run a dummy script during the docker build to pull down the model files.
# This bakes the model weights directly into the permanent layer of the image.
RUN python -c "from transformers import pipeline; pipeline('sentiment-analysis', model='distilbert-base-uncased-finetuned-sst-2-english')"

# Copy your actual application script
COPY app.py .

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```



## 2. How to Build and Run It:
Open your terminal inside the folder containing these files and execute the following commands:

### Step A: Build the Image
This step will take a couple of minutes because Docker is downloading the DistilBERT model weights from the Hugging Face Hub and embedding them into the layer structure.


```docker build -t hf-sentiment-api .```


### Step B: Launch the API Container

```docker run -d -p 8000:8000 --name sentiment-service hf-sentiment-api```

(Notice how fast it boots up! Because the model is already saved in the image, it doesn't need to fetch anything from the internet at startup.)


## 3. Test the API:
Send a payload containing a sentence to your containerized API:

```
curl -X POST "http://localhost:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{"text": "I absolutely love containerizing my machine learning workflows with Docker!"}'
```

Expected Response (JSON):
```{
  "text": "I absolutely love containerizing my machine learning workflows with Docker!",
  "sentiment": "POSITIVE",
  "confidence": 0.9997
}
```