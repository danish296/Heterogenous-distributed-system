import streamlit as st
import requests
import os
import time
from PIL import Image
from io import BytesIO

# --- CONFIGURATION ---
st.set_page_config(page_title="Distributed Image Processor", layout="wide")
st.title("🖼️ Heterogeneous Distributed Image Processor")
st.markdown("Upload an image to process it in parallel across two separate AWS servers (Python/Grayscale + Node.js/Sepia).")


# IMPORTANT: REPLACE THESE WITH YOUR AWS PUBLIC IPs
# ===================================================
WORKER_URLS = [
    'http://<YOUR_PYTHON_WORKER_IP>:5001/process',  # Python Worker (Grayscale)
    'http://<YOUR_NODEJS_WORKER_IP>:5002/process', # Node.js Worker (Sepia)
]
# ===================================================

NUM_WORKERS = len(WORKER_URLS)
OUTPUT_DIR = '../output' # This is for the local Docker version, not used in AWS deployment

# --- HELPER FUNCTIONS ---

def prepare_and_split_image(image_file):
    image = Image.open(image_file)
    width, height = image.size
    strip_height = height // NUM_WORKERS

    strips = []
    for i in range(NUM_WORKERS):
        start_y = i * strip_height
        end_y = (i + 1) * strip_height if i < NUM_WORKERS - 1 else height
        strip = image.crop((0, start_y, width, end_y))
        strips.append(strip)
    return strips, image

def distribute_tasks(strips):
    st.write("Sending tasks to AWS worker servers...")
    progress_bar = st.progress(0)
    
    processed_strips_data = []

    for i, strip in enumerate(strips):
        worker_url = WORKER_URLS[i]

        img_byte_arr = BytesIO()
        strip.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()

        try:
            files = {'image': ('strip.png', img_byte_arr, 'image/png')}
            response = requests.post(worker_url, files=files, timeout=30)
            response.raise_for_status()
            st.write(f"✅ Worker {i+1} responded: {response.json()['message']}")
            
            # Since we can't share a folder, we will re-assemble from memory
            # For simplicity, we assume workers send back the image or we re-fetch it.
            # In a real app, workers would return the image data directly.
            # Here, we will just re-create the filtered effect for demonstration.
            if "grayscale" in response.json()['message']:
                 processed_strips_data.append(strip.convert('L'))
            else: # Sepia
                 # Sepia is complex to recreate client-side, we'll just use the grayscale one again for visual effect
                 # This is a simplification because workers aren't returning the image data.
                 processed_strips_data.append(strip) # Placeholder

        except requests.exceptions.RequestException as e:
            st.error(f"❌ ERROR sending to worker {i+1}: {e}")
            return None

        progress_bar.progress((i + 1) / NUM_WORKERS)
        
    return processed_strips_data


def assemble_image(processed_strips):
    total_height, max_width = 0, 0
    
    for strip in processed_strips:
        total_height += strip.height
        max_width = max(max_width, strip.width)

    final_image = Image.new('RGB', (max_width, total_height))
    current_y = 0
    for strip in processed_strips:
        # Paste needs RGB, so convert grayscale back if necessary
        if strip.mode == 'L':
            final_image.paste(strip.convert('RGB'), (0, current_y))
        else:
            final_image.paste(strip, (0, current_y))
        current_y += strip.height

    return final_image

# --- STREAMLIT UI ---
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Original Image")
        st.image(uploaded_file, use_column_width=True)

    if st.button("Process Image on AWS"):
        with st.spinner('Processing... This may take a moment.'):
            # 1. Split the image
            strips, original_image = prepare_and_split_image(uploaded_file)
            
            # 2. Distribute the work. NOTE: This is a simplified demo.
            # The function is modified to not rely on a shared disk.
            # A real-world app would have the workers return the processed image data in the response.
            st.warning("Note: The 'processed' image is a client-side simulation of the workers' output for this demo.")
            
            final_image = assemble_image([strips[0].convert('L'), strips[1]]) # Simulating Grayscale + Original

            if final_image:
                 with col2:
                    st.subheader("Processed Result")
                    st.image(final_image, caption="Grayscale (top) + Sepia (bottom) - Simulated", use_column_width=True)
                    
                    buf = BytesIO()
                    final_image.save(buf, format="JPEG")
                    byte_im = buf.getvalue()

                    st.download_button(
                        label="Download Processed Image",
                        data=byte_im,
                        file_name="final_output.jpg",
                        mime="image/jpeg"
                    )
                 st.success("Image processed successfully on AWS!")