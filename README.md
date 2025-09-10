# Qwen AI Models Deployment Suite

This repository contains containerized deployments for two Qwen AI models with production-ready configurations and web interfaces.

## Projects

### 🎨 Qwen-Image

High-quality image generation from text prompts with multi-language support and multiple aspect ratios.

**[📖 Setup & Usage Guide →](qwen-image/README.md)**

### 🤖 Qwen2.5-VL  

Vision-language model for image/video analysis with multi-modal conversations and OpenAI-compatible API.

**[📖 Setup & Usage Guide →](qwen-vl/README.md)**

## Repository Structure

```text
├── qwen-image/           # Image generation service
│   ├── backend/         # FastAPI service
│   ├── streamlit-frontend/  # Web UI
│   ├── k8s-manifests/   # Kubernetes configs
│   └── README.md        # Complete setup guide
├── qwen-vl/             # Vision-language service  
│   ├── streamlit_app.py # Testing interface
│   ├── deployment.yaml  # Kubernetes config
│   └── README.md        # Complete setup guide
└── README.md            # This overview
```

## Quick Overview

| Service | Purpose | GPU Requirements | Deployment |
|---------|---------|------------------|------------|
| **Qwen-Image** | Text-to-image generation | 4x NVIDIA GPUs | Docker Compose + K8s |
| **Qwen2.5-VL** | Vision-language analysis | 1x NVIDIA GPU | Kubernetes + vLLM |

## Getting Started

Each project has its own complete documentation with setup instructions, API usage, and deployment guides. Choose the service you need and follow its README for detailed instructions.

## License

Apache 2.0 License (following the respective Qwen model licenses)
