import streamlit as st
import requests
import os
import time
from PIL import Image
from io import BytesIO

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Distributed Task Processor", layout="wide")
st.title("🚀 Heterogeneous Distributed Task Processor")
st.markdown("Select a task and provide an input to see it processed by a specialized microservice.")

# --- WORKER URLS (Centralized Dictionary) ---
WORKER_URLS = {
    "image_grayscale": 'http://localhost:5001/process',
    "image_sepia": 'http://localhost:5002/process',
    "math_primes": 'http://localhost:5003/calculate'
}
OUTPUT_DIR = '../output'

# --- IMAGE PROCESSING HELPER FUNCTIONS ---

def prepare_and_split_image(image_file):
    """Loads an image, splits it into two horizontal strips."""
    image = Image.open(image_file)
    width, height = image.size
    num_strips = 2  # Hardcoded for the two image workers
    strip_height = height // num_strips

    strips = []
    for i in range(num_strips):
        start_y = i * strip_height
        end_y = (i + 1) * strip_height if i < num_strips - 1 else height
        strip = image.crop((0, start_y, width, end_y))
        strips.append(strip)
    return strips

def distribute_image_tasks(strips):
    """Sends each image strip to its respective worker."""
    st.write("Sending image tasks to workers...")
    progress_bar = st.progress(0)
    
    image_worker_urls = [WORKER_URLS["image_grayscale"], WORKER_URLS["image_sepia"]]
    
    for i, strip in enumerate(strips):
        worker_url = image_worker_urls[i]
        
        # Convert PIL image to bytes for sending
        img_byte_arr = BytesIO()
        strip.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()

        try:
            files = {'image': ('strip.png', img_byte_arr, 'image/png')}
            response = requests.post(worker_url, files=files, timeout=30)
            response.raise_for_status()
            st.write(f"✅ Worker {i+1} responded: {response.json()['message']}")
        except requests.exceptions.RequestException as e:
            st.error(f"❌ ERROR sending to worker {i+1}: {e}")
            return False
        
        progress_bar.progress((i + 1) / len(strips))
    return True

def assemble_image():
    """Waits and assembles the processed image strips from the shared volume."""
    time.sleep(2)  # Give workers a moment to save files
    processed_strips = []
    total_height, max_width = 0, 0

    for i in range(2): # For the two image workers
        strip_path = os.path.join(OUTPUT_DIR, f'worker{i+1}', 'processed.png')
        if os.path.exists(strip_path):
            strip_img = Image.open(strip_path)
            processed_strips.append(strip_img)
            total_height += strip_img.height
            max_width = max(max_width, strip_img.width)
        else:
            st.error(f"Processed strip not found for worker {i+1}. The worker may have failed.")
            return None
    
    final_image = Image.new('RGB', (max_width, total_height))
    current_y = 0
    for strip in processed_strips:
        final_image.paste(strip, (0, current_y))
        current_y += strip.height
    
    return final_image

# --- MAIN STREAMLIT UI ---

task_choice = st.selectbox(
    "Select a Task:",
    ("Image Processing", "Mathematical Task (Find Primes)")
)

# ============================================
# UI for Image Processing
# ============================================
if task_choice == "Image Processing":
    st.header("🖼️ Image Processing")
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Original Image")
            st.image(uploaded_file, use_column_width=True)

        if st.button("Process Image"):
            with st.spinner('Distributing tasks to workers...'):
                strips = prepare_and_split_image(uploaded_file)
                success = distribute_image_tasks(strips)
                
                if success:
                    final_image = assemble_image()
                    if final_image:
                        with col2:
                            st.subheader("Processed Result")
                            st.image(final_image, caption="Grayscale (top) + Sepia (bottom)", use_column_width=True)
                            
                            # Convert image to a byte stream for downloading
                            buf = BytesIO()
                            final_image.save(buf, format="JPEG")
                            byte_im = buf.getvalue()

                            st.download_button(
                                label="Download Processed Image",
                                data=byte_im,
                                file_name="final_output.jpg",
                                mime="image/jpeg"
                            )
                        st.success("Image processed successfully!")

# ============================================
# UI for Mathematical Task
# ============================================
elif task_choice == "Mathematical Task (Find Primes)":
    st.header("🔢 Find Prime Numbers in a Range")
    
    col1, col2 = st.columns(2)
    with col1:
        start_num = st.number_input("Start Number:", min_value=1, value=1)
    with col2:
        end_num = st.number_input("End Number:", min_value=start_num, value=1000)

    if st.button("Calculate Primes"):
        if end_num > start_num:
            with st.spinner("Sending task to math worker..."):
                try:
                    payload = {"start": start_num, "end": end_num}
                    response = requests.post(WORKER_URLS["math_primes"], json=payload, timeout=60)
                    response.raise_for_status()
                    
                    result = response.json()
                    st.success("Calculation Complete!")
                    st.write(f"Found **{result['prime_count']}** prime numbers between {start_num} and {end_num}.")
                    st.json(result['primes']) # Display primes in a nice scrollable box

                except requests.exceptions.RequestException as e:
                    st.error(f"Error connecting to the math worker: {e}")
        else:
            st.warning("End number must be greater than start number.")