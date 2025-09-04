import requests
import os
import time
from PIL import Image

# --- CONFIGURATION ---
SOURCE_IMAGE_PATH = 'source.jpg'
OUTPUT_IMAGE_PATH = 'final_output.jpg'
WORKER_URLS = [
    'http://localhost:5001/process',  # Python Worker (Grayscale)
    'http://localhost:5002/process',  # Node.js Worker (Sepia)
]
NUM_WORKERS = len(WORKER_URLS)
OUTPUT_DIR = '../output'

def prepare_and_split_image():
    print(f"Loading source image: {SOURCE_IMAGE_PATH}")
    if not os.path.exists(SOURCE_IMAGE_PATH):
        print(f"Error: Add an image named 'source.jpg' to the coordinator folder.")
        return None

    # Clear previous output directories
    for i in range(NUM_WORKERS):
        worker_output_dir = os.path.join(OUTPUT_DIR, f'worker{i+1}')
        if not os.path.exists(worker_output_dir):
            os.makedirs(worker_output_dir)
        for f in os.listdir(worker_output_dir):
            os.remove(os.path.join(worker_output_dir, f))

    image = Image.open(SOURCE_IMAGE_PATH)
    width, height = image.size
    strip_height = height // NUM_WORKERS

    strips = []
    print("Splitting image into horizontal strips...")
    for i in range(NUM_WORKERS):
        start_y = i * strip_height
        end_y = (i + 1) * strip_height if i < NUM_WORKERS - 1 else height
        strip = image.crop((0, start_y, width, end_y))
        strips.append(strip)
    return strips

def distribute_tasks(strips):
    temp_strip_paths = []
    for i, strip in enumerate(strips):
        worker_url = WORKER_URLS[i]
        temp_path = f'temp_strip_{i}.png'
        strip.save(temp_path)
        temp_strip_paths.append(temp_path)

        print(f"Sending strip {i+1} to worker at {worker_url}...")
        try:
            with open(temp_path, 'rb') as f:
                response = requests.post(worker_url, files={'image': f}, timeout=30)
                response.raise_for_status()
            print(f"  -> Worker {i+1} responded: {response.json()['message']}")
        except requests.exceptions.RequestException as e:
            print(f"  -> ERROR sending to worker {i+1}: {e}")

    for path in temp_strip_paths:
        os.remove(path)

def assemble_image():
    print("\nWaiting a few seconds for workers to save files...")
    time.sleep(3) 

    processed_strips = []
    total_height = 0
    max_width = 0

    print("Fetching processed strips...")
    for i in range(NUM_WORKERS):
        strip_path = os.path.join(OUTPUT_DIR, f'worker{i+1}', 'processed.png')
        if os.path.exists(strip_path):
            strip_img = Image.open(strip_path)
            processed_strips.append(strip_img)
            total_height += strip_img.height
            if strip_img.width > max_width:
                max_width = strip_img.width
        else:
            print(f"Error: Processed strip not found for worker {i+1}")
            return

    if len(processed_strips) != NUM_WORKERS:
        print("Missing processed strips. Aborting assembly.")
        return

    print("Stitching images back together...")
    final_image = Image.new('RGB', (max_width, total_height))
    current_y = 0
    for strip in processed_strips:
        final_image.paste(strip, (0, current_y))
        current_y += strip.height

    final_image.save(OUTPUT_IMAGE_PATH)
    print(f"\n✅ Success! Final image saved to '{OUTPUT_IMAGE_PATH}'")

if __name__ == '__main__':
    image_strips = prepare_and_split_image()
    if image_strips:
        distribute_tasks(image_strips)
        assemble_image()