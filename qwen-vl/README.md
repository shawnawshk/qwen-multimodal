# Qwen2.5-VL Deployment

A containerized deployment of the Qwen2.5-VL-7B-Instruct model using vLLM with OpenAI-compatible API for vision-language tasks including image analysis, video understanding, and multi-modal conversations.

## 🤖 Features

- **Vision-Language Model** for image and video analysis
- **Multi-modal conversations** with images, videos, and text
- **vLLM backend** with high-performance inference
- **OpenAI-compatible API** for easy integration
- **Streamlit testing interface** with comprehensive UI
- **Batch processing** for multiple images
- **Video analysis capabilities** (with limitations)
- **Kubernetes deployment** for production scaling

## 🛠️ Quick Start

### Prerequisites

- Kubernetes cluster with GPU nodes
- NVIDIA GPU with 8GB+ VRAM
- kubectl configured for your cluster
- Python 3.8+ (for local Streamlit interface)

### Production Deployment

1. **Deploy to Kubernetes:**
   ```bash
   kubectl apply -f deployment.yaml
   ```

2. **Verify deployment:**
   ```bash
   kubectl get pods -l app=qwen-vl
   kubectl logs -l app=qwen-vl
   ```

3. **Port forward for testing:**
   ```bash
   kubectl port-forward service/qwen-vl 8000:80
   ```

### Local Testing Interface

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Streamlit interface:**
   ```bash
   streamlit run streamlit_app.py
   ```

3. **Access interface:**
   - **Web UI**: http://localhost:8501
   - **Configure endpoint**: Point to your vLLM service

## 🚀 API Usage

### OpenAI-Compatible Endpoints

The service provides OpenAI-compatible chat completions API:

#### Single Image Analysis
```bash
curl -X POST "http://localhost:8000/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen/Qwen2.5-VL-7B-Instruct",
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "image_url",
            "image_url": {
              "url": "data:image/jpeg;base64,<base64_encoded_image>"
            }
          },
          {
            "type": "text",
            "text": "Describe this image in detail."
          }
        ]
      }
    ],
    "max_tokens": 512,
    "temperature": 0.7
  }'
```

#### Multiple Images Analysis
```bash
curl -X POST "http://localhost:8000/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen/Qwen2.5-VL-7B-Instruct",
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "image_url",
            "image_url": {"url": "data:image/jpeg;base64,<image1_base64>"}
          },
          {
            "type": "image_url", 
            "image_url": {"url": "data:image/jpeg;base64,<image2_base64>"}
          },
          {
            "type": "text",
            "text": "Compare these two images and identify their similarities and differences."
          }
        ]
      }
    ],
    "max_tokens": 1024
  }'
```

#### Text-Only Conversation
```bash
curl -X POST "http://localhost:8000/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen/Qwen2.5-VL-7B-Instruct",
    "messages": [
      {
        "role": "user",
        "content": "Explain the concept of computer vision in simple terms."
      }
    ],
    "max_tokens": 512
  }'
```

### Available Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Service health status |
| `/v1/models` | GET | List available models |
| `/v1/chat/completions` | POST | Chat completions (OpenAI compatible) |

### Request Parameters

#### Required Parameters
- `model` (string): Model identifier ("Qwen/Qwen2.5-VL-7B-Instruct")
- `messages` (array): Conversation messages with content

#### Optional Parameters
- `max_tokens` (int): Maximum tokens to generate (default: 512)
- `temperature` (float): Sampling temperature 0.0-2.0 (default: 0.7)
- `top_p` (float): Nucleus sampling parameter 0.0-1.0 (default: 0.8)
- `stream` (bool): Enable streaming responses (default: false)

### Message Content Types

#### Text Content
```json
{
  "type": "text",
  "text": "Your question or instruction here"
}
```

#### Image Content
```json
{
  "type": "image_url",
  "image_url": {
    "url": "data:image/jpeg;base64,<base64_encoded_image>"
  }
}
```

#### Video Content (Limited Support)
```json
{
  "type": "video",
  "video": "data:video/mp4;base64,<base64_encoded_video>"
}
```

## 🖥️ Streamlit Testing Interface

The included Streamlit interface provides comprehensive testing capabilities:

### Interface Tabs

#### 1. Single Image Analysis
- **Upload individual images** (PNG, JPG, JPEG)
- **Ask questions** about the image content
- **Real-time analysis** with model responses
- **Copy responses** for further use

#### 2. Multiple Images Analysis  
- **Upload multiple images** simultaneously
- **Compare and analyze** relationships between images
- **Batch processing** with single prompt
- **Visual grid display** of uploaded images

#### 3. Video Analysis (Limited)
- **Video upload** support (MP4, AVI, MOV, WebM)
- **Frame extraction guidance** for workarounds
- **Metadata analysis** when direct processing unavailable
- **FFmpeg commands** for frame extraction

#### 4. Text Chat
- **Pure text conversations** with the model
- **Chat history** maintenance
- **Streaming responses** (if enabled)
- **Clear chat** functionality

### Configuration Options

- **Model Endpoint**: Configure vLLM service URL
- **Max Tokens**: Control response length (50-2048)
- **Temperature**: Adjust creativity (0.0-2.0)
- **Top P**: Control diversity (0.0-1.0)
- **Health Monitoring**: Check service status

## 🚢 Production Deployment

### Kubernetes Configuration

The deployment includes:

```yaml
# Key configuration from deployment.yaml
spec:
  containers:
    - name: model
      image: vllm/vllm-openai:latest
      command: ["vllm", "serve"]
      args:
        - "Qwen/Qwen2.5-VL-7B-Instruct"
        - "--host=0.0.0.0"
        - "--port=8000"
        - '--limit-mm-per-prompt={"image":2,"video":1}'
      resources:
        limits:
          nvidia.com/gpu: "1"
```

### Resource Requirements

#### Production Configuration
- **Node Type**: g6e.2xlarge or equivalent
- **GPUs**: 1x NVIDIA GPU (24GB+ VRAM recommended)
- **Memory**: Standard (managed by vLLM)
- **Storage**: Persistent volume for model cache
- **Shared Memory**: 20Gi for tensor operations

#### Multi-Modal Limits
- **Images per prompt**: 2 (configurable)
- **Videos per prompt**: 1 (limited support)
- **Total context**: Managed by vLLM automatically

### Environment Configuration

```yaml
env:
  - name: CUDA_VISIBLE_DEVICES
    value: "0"
  - name: VLLM_WORKER_MULTIPROC_METHOD
    value: "spawn"
```

### Volume Mounts

```yaml
volumeMounts:
  - mountPath: /root/.cache/huggingface
    name: cache-volume
  - name: shm
    mountPath: /dev/shm
```

## 📊 Performance Optimization

### Inference Performance
- **Model loading**: 30-60s initial startup
- **Single image**: 2-10s response time
- **Multiple images**: 5-20s depending on complexity
- **Text-only**: 1-5s response time

### Memory Management
- **Automatic batching**: vLLM handles request batching
- **Memory optimization**: Dynamic memory allocation
- **GPU utilization**: Optimized for single GPU deployment

### Scaling Considerations
```yaml
# For higher throughput
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
```

## 🔍 Monitoring & Health Checks

### Health Endpoint Response
```json
{
  "status": "ok"
}
```

### Kubernetes Probes
- **Startup Probe**: TCP socket check, 30s delay, 60 failure threshold
- **Readiness Probe**: HTTP health check, 30s delay, 5s intervals
- **Liveness Probe**: HTTP health check, 60s delay, 10s intervals

### Monitoring Metrics
- Request rate and response latency
- GPU utilization and memory usage
- Model loading status and errors
- Multi-modal content processing stats

## 🎯 Use Cases & Examples

### Image Analysis Tasks
```python
# Object detection and description
"What objects can you see in this image? List them with their locations."

# Scene understanding
"Describe the setting, mood, and atmosphere of this scene."

# Text extraction
"What text is visible in this image? Transcribe it exactly."

# Visual reasoning
"Based on what you see, what might happen next in this scene?"
```

### Multi-Image Comparison
```python
# Before/after analysis
"Compare these before and after photos. What changes do you notice?"

# Product comparison
"Compare these two products. What are the key differences?"

# Style analysis
"Analyze the artistic styles in these images. How do they differ?"
```

### Video Analysis (with workarounds)
```bash
# Extract frames for analysis
ffmpeg -i video.mp4 -vf fps=1 frame_%03d.jpg

# Extract key moments
ffmpeg -i video.mp4 -vf "select=not(mod(n\,30))" -vsync vfr frame_%03d.jpg
```

## ⚠️ Current Limitations

### Video Processing
- **vLLM limitation**: OpenAI-compatible API doesn't fully support video processing
- **Workaround**: Extract frames using FFmpeg and analyze as images
- **Future support**: Native video processing may be added in future vLLM versions

### Multi-Modal Constraints
- **Image limit**: 2 images per prompt (configurable)
- **Video limit**: 1 video per prompt (limited functionality)
- **Context length**: Managed automatically by vLLM

### Performance Considerations
- **Cold start**: Initial model loading takes time
- **Memory usage**: Large images consume more GPU memory
- **Batch processing**: Limited by GPU memory capacity

## 🐛 Troubleshooting

### Common Issues

#### Model Loading Failures
```bash
# Check GPU availability
kubectl exec -it <pod-name> -- nvidia-smi

# Check model download
kubectl logs <pod-name> | grep -i "loading\|download"

# Verify storage permissions
kubectl describe pv <pv-name>
```

#### API Connection Issues
```bash
# Test health endpoint
curl -f http://localhost:8000/health

# Check service connectivity
kubectl get svc qwen-vl
kubectl describe svc qwen-vl

# Port forwarding for debugging
kubectl port-forward svc/qwen-vl 8000:80
```

#### Image Processing Errors
```bash
# Check image encoding
python -c "
import base64
with open('image.jpg', 'rb') as f:
    encoded = base64.b64encode(f.read()).decode()
    print(f'Image size: {len(encoded)} characters')
"

# Verify image format
file image.jpg
```

### Debug Commands

```bash
# Monitor pod status
kubectl get pods -l app=qwen-vl -w

# View detailed logs
kubectl logs -f deployment/qwen-vl

# Check resource usage
kubectl top pods -l app=qwen-vl

# Describe pod for events
kubectl describe pod <pod-name>
```

### Performance Tuning

#### For Better Response Times
```yaml
# Increase resource limits
resources:
  limits:
    nvidia.com/gpu: "1"
    memory: "32Gi"
  requests:
    nvidia.com/gpu: "1"
    memory: "16Gi"
```

#### For Higher Throughput
```yaml
# Enable tensor parallelism (if multiple GPUs)
args:
  - "--tensor-parallel-size=2"
  - "--pipeline-parallel-size=1"
```

## 🧪 Testing

### Basic Functionality Test
```bash
# Test health
curl http://localhost:8000/health

# Test text-only chat
curl -X POST "http://localhost:8000/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen/Qwen2.5-VL-7B-Instruct",
    "messages": [{"role": "user", "content": "Hello, how are you?"}],
    "max_tokens": 50
  }'
```

### Image Analysis Test
```python
import base64
import requests

# Encode test image
with open("test_image.jpg", "rb") as f:
    image_base64 = base64.b64encode(f.read()).decode()

# Test API call
response = requests.post("http://localhost:8000/v1/chat/completions", json={
    "model": "Qwen/Qwen2.5-VL-7B-Instruct",
    "messages": [{
        "role": "user",
        "content": [
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}},
            {"type": "text", "text": "Describe this image"}
        ]
    }],
    "max_tokens": 200
})

print(response.json())
```

### Load Testing
```bash
# Install testing tools
pip install locust

# Run load test
locust -f test_load.py --host http://localhost:8000
```

## 📄 Model Information

### Qwen2.5-VL Capabilities
- **Image understanding** with detailed analysis
- **Video processing** (limited in current deployment)
- **Multi-turn conversations** with visual context
- **Text extraction** from images
- **Visual reasoning** and inference
- **Multi-language support** (primarily English/Chinese)

### Technical Specifications
- **Model Size**: 7B parameters
- **Context Length**: Variable (managed by vLLM)
- **Input Modalities**: Text, Images, Videos
- **Output**: Text responses
- **Architecture**: Vision-Language Transformer
- **Training**: Multi-modal instruction tuning

## 📚 Additional Resources

- **Model Card**: [Qwen2.5-VL on Hugging Face](https://huggingface.co/Qwen/Qwen2.5-VL-7B-Instruct)
- **vLLM Documentation**: [vLLM OpenAI Server](https://docs.vllm.ai/en/latest/serving/openai_compatible_server.html)
- **Paper**: [Qwen2.5 Technical Report](https://arxiv.org/abs/2409.12191)
- **Examples**: See Streamlit interface for interactive examples

## 📞 Support

For Qwen2.5-VL specific issues:

1. **Check the troubleshooting section** above
2. **Review vLLM and pod logs** for error details
3. **Verify GPU resources** and model loading
4. **Test with simple text prompts** first
5. **Use Streamlit interface** for interactive debugging
6. **Open an issue** with detailed reproduction steps

---

**Note**: Video processing capabilities are currently limited due to vLLM's OpenAI-compatible API constraints. For full video analysis, consider using the native Qwen2.5-VL API or extract frames for image-based analysis.