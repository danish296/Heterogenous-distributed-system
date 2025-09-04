import streamlit as st
import requests
from PIL import Image
from io import BytesIO

st.set_page_config(page_title="Distributed Image Processor", layout="wide")
st.title("🖼️ True Distributed Image Processor")
st.markdown("Upload an image to process it in parallel across two separate AWS servers. The workers now return the processed image data directly.")

# IMPORTANT: REPLACE THESE WITH YOUR AWS PUBLIC IPs
# ===================================================
WORKER_URLS = [
    'http://<YOUR_PYTHON_WORKER_IP>:5001/process',  # Python Worker (Grayscale)
    'http://<YOUR_NODEJS_WORKER_IP>:5002/process', # Node.js Worker (Sepia)
]
# ===================================================

def prepare_and_split_image(image_file):
    image = Image.open(image_file)
    width, height = image.size
    strip_height = height // 2
    strips = [
        image.crop((0, 0, width, strip_height)),
        image.crop((0, strip_height, width, height))
    ]
    return strips, image

def distribute_and_get_results(strips):
    st.write("Sending tasks to AWS worker servers...")
    progress_bar = st.progress(0)
    processed_strips = []

    for i, strip in enumerate(strips):
        worker_url = WORKER_URLS[i]
        
        img_byte_arr = BytesIO()
        strip.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()

        try:
            files = {'image': ('strip.png', img_byte_arr, 'image/png')}
            response = requests.post(worker_url, files=files, timeout=30)
            response.raise_for_status()

            # THIS IS THE KEY: Directly read the returned image data
            processed_strip = Image.open(BytesIO(response.content))
            processed_strips.append(processed_strip)
            st.write(f"✅ Worker {i+1} successfully returned processed image.")
        
        except requests.exceptions.RequestException as e:
            st.error(f"❌ ERROR communicating with worker {i+1}: {e}")
            return None
        
        progress_bar.progress((i + 1) / len(strips))
    
    return processed_strips

def assemble_image(processed_strips):
    max_width = max(p.width for p in processed_strips)
    total_height = sum(p.height for p in processed_strips)
    
    final_image = Image.new('RGB', (max_width, total_height))
    current_y = 0
    for strip in processed_strips:
        # Paste needs RGB, so convert non-RGB images before pasting
        final_image.paste(strip.convert('RGB') if strip.mode != 'RGB' else strip, (0, current_y))
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
            strips, original_image = prepare_and_split_image(uploaded_file)
            processed_strips = distribute_and_get_results(strips)
            
            if processed_strips and len(processed_strips) == 2:
                final_image = assemble_image(processed_strips)
                with col2:
                    st.subheader("Processed Result")
                    # Let's use the invert caption for clarity
                    st.image(final_image, caption="Grayscale (top) + Inverted Colors (bottom)", use_column_width=True)
                    
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
