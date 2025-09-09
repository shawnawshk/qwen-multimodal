vllm bench serve \
  --host qwen-vl \
  --port 80 \
  --backend openai-chat \
  --endpoint /v1/chat/completions \
  --endpoint-type openai-chat \
  --model Qwen/Qwen2.5-VL-7B-Instruct \
  --dataset-name hf \
  --dataset-path lmarena-ai/VisionArena-Chat \
  --num-prompts 128
