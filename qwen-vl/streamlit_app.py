import streamlit as st
import requests
import base64
import json
from PIL import Image
import io
import tempfile
import os
from typing import List, Dict, Any

# Configure Streamlit page
st.set_page_config(
    page_title="Qwen2.5-VL Model Tester",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    .uploadedFile {
        border: 2px dashed #667eea;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        background-color: #f8f9ff;
    }
    
    .stTextArea > div > div > textarea {
        border-radius: 8px;
        border: 2px solid #e1e5e9;
        font-family: -apple-system, BlinkMacSystemFont, sans-serif;
        font-size: 14px;
        line-height: 1.6;
        background-color: #fafbfc;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
        background-color: #ffffff;
    }
    
    /* Special styling for response text areas */
    div[data-testid="stTextArea"] textarea {
        background-color: #f8f9fa;
        border: 2px solid #dee2e6;
        color: #495057;
        cursor: text;
    }
    
    div[data-testid="stTextArea"] textarea:focus {
        border-color: #80bdff;
        box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
        background-color: #ffffff;
    }
    
    .response-container {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# App title and description
st.title("🤖 Qwen2.5-VL Model Tester")
st.markdown("Test your deployed Qwen2.5-VL model with images, videos, and text conversations")

# Sidebar configuration
st.sidebar.header("⚙️ Configuration")

# Model endpoint configuration
model_endpoint = st.sidebar.text_input(
    "Model Endpoint", 
    value="http://localhost:8000",
    help="URL of your vLLM server"
)

# Model parameters
max_tokens = st.sidebar.slider("Max Tokens", 50, 2048, 512)
temperature = st.sidebar.slider("Temperature", 0.0, 2.0, 0.7, 0.1)
top_p = st.sidebar.slider("Top P", 0.0, 1.0, 0.8, 0.1)

# Helper functions
def encode_image_to_base64(image_file) -> str:
    """Convert uploaded image to base64 string"""
    if image_file is not None:
        image = Image.open(image_file)
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return f"data:image/jpeg;base64,{img_str}"
    return None

def encode_video_to_base64(video_file) -> str:
    """Convert uploaded video to base64 string"""
    if video_file is not None:
        video_bytes = video_file.read()
        video_str = base64.b64encode(video_bytes).decode()
        # Reset file pointer for potential reuse
        video_file.seek(0)
        return f"data:video/mp4;base64,{video_str}"
    return None

def call_vllm_api(messages: List[Dict], model_endpoint: str, **kwargs) -> str:
    """Call the vLLM OpenAI-compatible API"""
    try:
        url = f"{model_endpoint}/v1/chat/completions"
        
        payload = {
            "model": "Qwen/Qwen2.5-VL-7B-Instruct",
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", 512),
            "temperature": kwargs.get("temperature", 0.7),
            "top_p": kwargs.get("top_p", 0.8),
            "stream": False
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
        
    except requests.exceptions.RequestException as e:
        return f"Error calling API: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"

# Main interface tabs
tab1, tab2, tab3, tab4 = st.tabs(["📷 Single Image", "🖼️ Multiple Images", "🎥 Video Analysis", "💬 Text Chat"])

# Tab 1: Single Image Analysis
with tab1:
    st.header("Single Image Analysis")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Upload Image")
        uploaded_image = st.file_uploader(
            "Choose an image...", 
            type=['png', 'jpg', 'jpeg'],
            key="single_image"
        )
        
        if uploaded_image:
            image = Image.open(uploaded_image)
            st.image(image, caption="Uploaded Image", width="stretch")
        
        st.subheader("Your Question")
        user_question = st.text_area(
            "What would you like to know about this image?",
            value="Describe this image in detail.",
            height=100,
            key="single_question"
        )
        
        if st.button("🚀 Analyze Image", key="analyze_single"):
            if uploaded_image and user_question:
                with st.spinner("Analyzing image..."):
                    # Prepare message with image
                    image_base64 = encode_image_to_base64(uploaded_image)
                    
                    messages = [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": image_base64
                                    }
                                },
                                {
                                    "type": "text",
                                    "text": user_question
                                }
                            ]
                        }
                    ]
                    
                    response = call_vllm_api(
                        messages, 
                        model_endpoint,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        top_p=top_p
                    )
                    
                    st.session_state.single_response = response
            else:
                st.warning("Please upload an image and enter a question.")
    
    with col2:
        st.subheader("Model Response")
        if hasattr(st.session_state, 'single_response'):
            st.markdown("**🤖 AI Response:**")
            # Create a nice response display
            response_container = st.container()
            with response_container:
                st.text_area(
                    label="AI Response",
                    value=st.session_state.single_response,
                    height=350,
                    disabled=False,
                    label_visibility="collapsed",
                    key="single_response_display"
                )
                # Add copy button
                if st.button("📋 Copy Response", key="copy_single"):
                    st.success("Response copied to clipboard! (Use Ctrl+A, Ctrl+C in the text area above)")
        else:
            st.info("🔍 Upload an image and click 'Analyze Image' to see the AI response here.")

# Tab 2: Multiple Images Analysis
with tab2:
    st.header("Multiple Images Analysis")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Upload Multiple Images")
        uploaded_images = st.file_uploader(
            "Choose images...", 
            type=['png', 'jpg', 'jpeg'],
            accept_multiple_files=True,
            key="multiple_images"
        )
        
        if uploaded_images:
            st.write(f"Uploaded {len(uploaded_images)} images:")
            cols = st.columns(min(len(uploaded_images), 3))
            for idx, img_file in enumerate(uploaded_images):
                with cols[idx % 3]:
                    image = Image.open(img_file)
                    st.image(image, caption=f"Image {idx+1}", width="stretch")
        
        st.subheader("Your Question")
        multi_question = st.text_area(
            "What would you like to know about these images?",
            value="Compare these images and identify their similarities and differences.",
            height=100,
            key="multi_question"
        )
        
        if st.button("🚀 Analyze Images", key="analyze_multiple"):
            if uploaded_images and multi_question:
                with st.spinner("Analyzing images..."):
                    # Prepare message with multiple images
                    content = []
                    
                    # Add all images
                    for img_file in uploaded_images:
                        image_base64 = encode_image_to_base64(img_file)
                        content.append({
                            "type": "image_url",
                            "image_url": {
                                "url": image_base64
                            }
                        })
                    
                    # Add text question
                    content.append({
                        "type": "text",
                        "text": multi_question
                    })
                    
                    messages = [
                        {
                            "role": "user",
                            "content": content
                        }
                    ]
                    
                    response = call_vllm_api(
                        messages, 
                        model_endpoint,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        top_p=top_p
                    )
                    
                    st.session_state.multi_response = response
            else:
                st.warning("Please upload at least one image and enter a question.")
    
    with col2:
        st.subheader("Model Response")
        if hasattr(st.session_state, 'multi_response'):
            st.markdown("**🤖 AI Response:**")
            # Create a nice response display
            response_container = st.container()
            with response_container:
                st.text_area(
                    label="AI Response",
                    value=st.session_state.multi_response,
                    height=350,
                    disabled=False,
                    label_visibility="collapsed",
                    key="multi_response_display"
                )
                # Add copy button
                if st.button("📋 Copy Response", key="copy_multi"):
                    st.success("Response copied to clipboard! (Use Ctrl+A, Ctrl+C in the text area above)")
        else:
            st.info("🔍 Upload images and click 'Analyze Images' to see the AI response here.")

# Tab 3: Video Analysis
with tab3:
    st.header("Video Analysis")
    st.warning("⚠️ Video analysis is currently limited. While video upload is enabled in your deployment, the vLLM OpenAI-compatible API doesn't fully support video content processing yet.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Upload Video")
        uploaded_video = st.file_uploader(
            "Choose a video...", 
            type=['mp4', 'avi', 'mov', 'webm'],
            key="video_file",
            help="Supported formats: MP4, AVI, MOV, WebM"
        )
        
        if uploaded_video:
            st.video(uploaded_video)
            
            # Show video info
            file_size = len(uploaded_video.getvalue()) / (1024 * 1024)  # Size in MB
            st.caption(f"📁 File: {uploaded_video.name} ({file_size:.1f} MB)")
        
        st.subheader("Your Question")
        video_question = st.text_area(
            "What would you like to know about this video?",
            value="Describe what happens in this video in detail.",
            height=100,
            key="video_question",
            help="Try asking about: actions, objects, scenes, timeline, emotions, etc."
        )
        
        # Video analysis options
        with st.expander("🔧 Frame Extraction (Workaround)"):
            st.markdown("**Since video processing isn't fully supported, try extracting frames:**")
            
            if uploaded_video:
                st.info("💡 **Suggested Workaround**: Extract frames from your video and use the 'Multiple Images' tab for analysis.")
                
                # Show extraction command
                video_name = uploaded_video.name.rsplit('.', 1)[0]
                st.code(f"""
# Extract 1 frame per second
ffmpeg -i "{uploaded_video.name}" -vf fps=1 {video_name}_frame_%03d.jpg

# Extract 5 key frames
ffmpeg -i "{uploaded_video.name}" -vf "select=not(mod(n\\,30))" -vsync vfr {video_name}_frame_%03d.jpg
                """, language="bash")
                
                st.markdown("Then upload the extracted frames to the **'Multiple Images'** tab for analysis.")
            else:
                st.markdown("Upload a video to see frame extraction commands.")
        
        if st.button("🚀 Try Video Analysis (Limited)", key="analyze_video"):
            if uploaded_video and video_question:
                with st.spinner("Attempting video analysis..."):
                    try:
                        # Since we know video processing doesn't work properly,
                        # provide a helpful response with video metadata
                        file_size = len(uploaded_video.getvalue()) / (1024 * 1024)
                        
                        messages = [
                            {
                                "role": "user",
                                "content": f"""I have a video file with the following details:
- Filename: {uploaded_video.name}
- Size: {file_size:.1f} MB
- Question: {video_question}

Since you cannot directly process video content through this interface, please provide:
1. General guidance on what to look for in a video when answering: "{video_question}"
2. Suggestions for extracting and analyzing video content
3. What specific frames or moments might be most relevant
4. Alternative approaches for video analysis"""
                            }
                        ]
                        
                        response = call_vllm_api(
                            messages, 
                            model_endpoint,
                            max_tokens=max_tokens,
                            temperature=temperature,
                            top_p=top_p
                        )
                        
                        st.session_state.video_response = f"""⚠️ **Video Content Analysis Not Available**

The model cannot directly view your video content through vLLM's OpenAI-compatible API. However, here's helpful guidance:

{response}

---
💡 **Recommended Workaround**: Extract key frames from your video and upload them to the 'Multiple Images' tab for visual analysis."""
                        
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                        st.session_state.video_response = f"""❌ **Analysis Failed**

Unable to process video analysis request. 

**Suggested alternatives:**
1. Extract frames using FFmpeg: `ffmpeg -i "{uploaded_video.name}" -vf fps=0.5 frame_%03d.jpg`
2. Upload extracted frames to the 'Multiple Images' tab
3. Use the native Qwen2.5-VL API directly (not through vLLM)

**Technical details:** vLLM's OpenAI-compatible API doesn't fully support video processing for Qwen2.5-VL yet."""
            else:
                st.warning("Please upload a video and enter a question.")
    
    with col2:
        st.subheader("Model Response")
        if hasattr(st.session_state, 'video_response'):
            st.markdown("**🤖 AI Response:**")
            # Create a nice response display
            response_container = st.container()
            with response_container:
                st.text_area(
                    label="AI Response",
                    value=st.session_state.video_response,
                    height=350,
                    disabled=False,
                    label_visibility="collapsed",
                    key="video_response_display"
                )
                # Add copy button
                if st.button("📋 Copy Response", key="copy_video"):
                    st.success("Response copied to clipboard! (Use Ctrl+A, Ctrl+C in the text area above)")
        else:
            st.info("🎥 Upload a video and click 'Analyze Video' to see the AI response here.")
            
            # Add some helpful tips
            with st.expander("💡 Current Video Limitations & Workarounds"):
                st.markdown("""
                **Current Status:**
                - ✅ Video upload is enabled in your deployment
                - ❌ vLLM's OpenAI API doesn't process video content yet
                - 🔄 The model receives metadata but can't "see" the video
                
                **Workarounds:**
                1. **Extract frames**: Use tools like FFmpeg to extract key frames as images
                2. **Use image analysis**: Upload individual frames to the "Single Image" or "Multiple Images" tabs
                3. **Direct API**: Use the native Qwen2.5-VL API instead of vLLM's OpenAI wrapper
                
                **Alternative approach:**
                ```bash
                # Extract frames from video
                ffmpeg -i your_video.mp4 -vf fps=1 frame_%03d.jpg
                ```
                Then upload the extracted frames to the image analysis tabs.
                """)

# Tab 4: Text Chat
with tab4:
    st.header("Text-Only Chat")
    
    # Initialize chat history
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    
    # Display chat messages
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to chat history
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Prepare messages for API call
                api_messages = [
                    {"role": msg["role"], "content": msg["content"]} 
                    for msg in st.session_state.chat_messages
                ]
                
                response = call_vllm_api(
                    api_messages,
                    model_endpoint,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p
                )
                
                st.markdown(response)
                
                # Add assistant response to chat history
                st.session_state.chat_messages.append({"role": "assistant", "content": response})
    
    # Clear chat button
    if st.button("🗑️ Clear Chat"):
        st.session_state.chat_messages = []
        st.rerun()

# Footer with model information
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Model Info")
st.sidebar.markdown("""
**Qwen2.5-VL-7B-Instruct**
- Vision-Language Model
- Supports images and videos
- Multi-modal conversations
- Agent capabilities
""")

# Health check
st.sidebar.markdown("---")
if st.sidebar.button("🔍 Check Model Health"):
    try:
        health_url = f"{model_endpoint}/health"
        response = requests.get(health_url, timeout=5)
        if response.status_code == 200:
            st.sidebar.success("✅ Model is healthy!")
        else:
            st.sidebar.error(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        st.sidebar.error(f"❌ Cannot reach model: {str(e)}")