# Multi-scale Agentic RAG Playbook

A sophisticated RAG (Retrieval-Augmented Generation) system that enables intelligent interaction with CVPR 2024 research papers at different levels of granularity. The system provides three distinct modes of operation: abstract-level search, detailed paper analysis, and intelligent routing between these information sources.

## Features

- RAG pipeline for CVPR 2024 paper abstracts
- Deep-dive analysis of individual papers through full-text RAG
- Intelligent query routing using LangGraph agents
- Dynamic database selection based on query complexity

## Prerequisites

- Python 3.10+
- NVIDIA API key from [build.nvidia.com](https://build.nvidia.com)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/NVIDIA-AI-Technology-Center/multi-scale-agentic-rag-playbook
cd multi-scale-agentic-rag-playbook
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your NVIDIA API key:
   - Create an account at [build.nvidia.com](https://build.nvidia.com)
   - Generate an API key
   - You will be asked to provide your key in the second cell of the notebook
