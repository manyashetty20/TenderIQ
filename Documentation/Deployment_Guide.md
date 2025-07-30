# TenderIQ Deployment Guide

**Platform-Specific Instructions: Windows | macOS | Linux
Repo** : https://github.com/manyashetty20/TenderIQ

## Summary

#### Component Technology

#### Frontend Streamlit

#### Backend FastAPI (served with Uvicorn)

#### LLMs Groq (cloud), LLaMA (local)

#### Storage JSON files, local folders

#### Model llama-cpp-python + .gguf OR Groq API

# 1. Windows Deployment Guide

### Prerequisites

```
● Python 3.9+ from python.org
```
```
● Git (from git-scm.com)
```
```
● Microsoft C++ Build Tools (for faiss-cpu)
```
```
● Optional: nssm for background services
```
### Setup Steps

```
a. Clone the repo
git clone https://github.com/manyashetty20/TenderIQ.git
cd TenderIQ
```

```
b. Create virtual environment
python -m venv env
```
```
c. Activate the environment
env\Scripts\activate
```
```
d. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```
```
e. Install Llama
https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/blob/main/llama-2-7b-chat.
Q4_K_M.gguf
```
### Environment Variables

Create a file .env in the root folder with the following:

GROQ_API_KEY=your_groq_api_key

### Run the App

**Start Backend**
uvicorn src.api.main:app --reload

**Start Frontend**
streamlit run app.py

Then go to: [http://localhost:](http://localhost:)

### Common Issues (Windows)

```
Issue Fix
```
```
faiss-cpu install
error
```
```
Install Build Tools for Visual Studio
```
```
.env not read Ensure you’ve installed python-dotenv and file is in project
root
```
Port already in use (^) Try another port using --port flag


# 2. macOS Deployment Guide

### Prerequisites

```
● Python 3.9+ (via python.org or brew install python@3.9)
```
```
● Git
```
```
● Homebrew (for optional system packages)
```
### Setup Steps

```
a. Clone the repository
git clone https://github.com/manyashetty20/TenderIQ.git
cd TenderIQ
```
```
b. Create virtual environment
python3 -m venv env
```
```
c. Activate it
source env/bin/activate
```
```
d. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```
```
e. Install Llama
https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/blob/main/llama-2-7b-chat.
Q4_K_M.gguf
```
```
If using Apple Silicon (M1/M2), Faiss and PyMuPDF may require additional build
tools:
```
```
brew install cmake pkg-config mupdf
pip install --no-binary :all: PyMuPDF
```
### Environment Variables

Create a .env file:

GROQ_API_KEY=your_groq_api_key


### Run the App

**Backend (Uvicorn)**
uvicorn src.api.main:app --reload

**Frontend (Streamlit)**
streamlit run app.py

Visit: [http://localhost:](http://localhost:)

### Common Issues (macOS)

```
Issue Fix
```
```
faiss not
installing
```
```
Use pip install faiss-cpu or compile manually if needed
```
M1 chip issues (^) Use universal wheels or build from source (brew install
mupdf)
.env not loaded Ensure it's in the root folder and you're using dotenv

# 3. Linux Deployment Guide (Ubuntu,

# Debian, Arch, etc.)

### Prerequisites

```
● Python 3.9+ (sudo apt install python3 python3-venv)
```
```
● Git
```
```
● pip (sudo apt install python3-pip)
```
```
● curl/wget for model downloads
```
### Setup Steps

```
a. Clone the repo
git clone https://github.com/manyashetty20/TenderIQ.git
cd TenderIQ
```

```
b. Create virtual environment
python3 -m venv env
```
```
c. Activate environment
source env/bin/activate
```
```
d. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```
```
e. Install Llama
https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/blob/main/llama-2-7b-chat.
Q4_K_M.gguf
```
### Environment Variables

- Create a .env file
    nano .env

Example contents:

GROQ_API_KEY=your_groq_api_key

### Run the App

**Backend (Uvicorn)**
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

**Frontend (Streamlit)**

streamlit run app.py

Go to: [http://localhost:](http://localhost:)

### Common Issues (Linux)

```
Issue Fix
```
Permission errors (^) Use chmod or run as correct user
Uvicorn not found (^) Ensure env/bin is active
Missing system
libs
sudo apt install libmupdf-dev build-essential for
Faiss and PyMuPDF


## Final Checklist

```
● .env created and populated
```
```
● Virtual environment activated
```
```
● uvicorn backend running
```
```
● streamlit frontend running
```
```
● Model file (optional for LLaMA) exists and path is set
```
```
● Access http://localhost:8501 and verify end-to-end functionality
```

