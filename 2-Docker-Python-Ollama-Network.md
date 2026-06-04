# In this Example, we are going to access a container from another container
### Notice: This Image is > 6GB in size on a MacBook Pro.

To allow one Docker container to talk to another, the most reliable approach is to place them on the same user-defined Docker network. This enables automatic service discovery. This means our Python container can connect to the Ollama container simply by using the Ollama container's name as the URL hostname.

## Here is the complete setup to get our Python app communicating with our running Ollama container.

## 1- The Python Client Application:

Create a directory on your machine and add the following three files:
```app.py```

```
import requests
import sys

# Note: "ollama-container" will be the literal name of your running Ollama container
OLLAMA_API_URL = "http://ollama-container:11434/api/generate"

def ask_gemma(prompt):
    payload = {
        "model": "gemma3:1b",
        "prompt": prompt,
        "stream": False  # Keeps the response simple by turning off streaming chunks
    }
    
    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=60)
        response.raise_for_status()
        return response.json().get("response")
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Ollama container: {e}")
        sys.exit(1)

if __name__ == "__main__":
    prompt = "Why is Docker useful for microservices? Keep it to one sentence."
    print(f"Sending prompt to Gemma: '{prompt}'")
    
    answer = ask_gemma(prompt)
    print(f"\nGemma Response:\n{answer}")
```

```requirements.txt```

```
requests==2.31.0
```


```Dockerfile```
```
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

CMD ["python", "app.py"]
```


## 2- The Ollama Container and Docker Network:

### Step A: Create a custom Docker network
```docker network create genai-network```

### Step B: Start an Ollama Container and Connect it to the Network:
You will need an Ollama container up and running, here's how you start it:

```docker run -d -v ollama:/root/.ollama -p 11434:11434 --network genai-network --name ollama-container ollama/ollama```

### Step C: Pull down the gemma3:1b Model Files:

After that, instruct the running Ollama engine to pull down the gemma3:1b model files as follows:

```docker exec -it ollama-container ollama run gemma3:1b```

(Once the download completes and the prompt opens, type ```/exit``` and hit Enter to jump back to your regular terminal).


### Step D: Build your Python image:
In the directory containing your new files, run:

```docker build -t python-gemma-client .```

### Step E: Run the Python app container on the same network

```docker run --rm --network genai-network python-gemma-client```

### How It Works Under the Hood:
Because both containers are pinned to ```genai-network```, Docker’s internal DNS intercepts the request to ```http://ollama-container```. It resolves it to the private IP address of your Ollama container automatically. 

The app completes its execution, prints Gemma's response right in your terminal, and safely destroys the client container (```--rm```), leaving your backend model engine up and running.