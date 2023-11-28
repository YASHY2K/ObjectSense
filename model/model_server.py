import os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from PIL import Image
import torch
import numpy as np
from model_utils import load_model, process_prediction, draw_boxes
from torchvision.transforms import functional as F

app = Flask(__name__)
CORS(app)

# Model configurations
coco_names = [
    '__background__', 'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus',
    'train', 'truck', 'boat', 'traffic light', 'fire hydrant', 'N/A', 'stop sign',
    'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow',
    'elephant', 'bear', 'zebra', 'giraffe', 'N/A', 'backpack', 'umbrella', 'N/A', 'N/A',
    'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball',
    'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket',
    'bottle', 'N/A', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl',
    'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza',
    'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed', 'N/A', 'dining table',
    'N/A', 'N/A', 'toilet', 'N/A', 'tv', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone',
    'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'N/A', 'book',
    'clock', 'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush', 'Camera'
]

COLORS = np.random.uniform(0, 255, size=(len(coco_names), 3))

UPLOAD_FOLDER = r'H:\DCSC\ObjectSense\upload_file\static\uploaded_images'
OUTPUT_FOLDER = r'H:\DCSC\ObjectSense\upload_file\static\outputs'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

# Load the model once
model_path = r'H:\DCSC\ObjectSense\model\retina_net.pkl'
model = load_model(model_path)

# Detection threshold
detection_threshold = 0.5

@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'})

    image = request.files['image']

    # Process the image
    img = Image.open(image).convert('RGB')
    img_tensor = F.to_tensor(img).unsqueeze(0)

    # Use the model for predictions
    with torch.no_grad():
        boxes, pred_classes = process_prediction(img_tensor, model, detection_threshold)

    # Process the prediction to draw bounding boxes on the image
    result_image = draw_boxes(np.array(img), boxes, pred_classes, coco_names, COLORS)

    # Save the result image with the received timestamp
    timestamp = request.form.get('timestamp', None)
    if timestamp:
        result_image_filename = f'{float(timestamp):.0f}_result_image.jpg'
        result_image_path = os.path.join(app.config['OUTPUT_FOLDER'], result_image_filename)
        result_image.save(result_image_path)

        return jsonify({'result_image': result_image_filename})
    else:
        return jsonify({'error': 'No timestamp provided'})

if __name__ == '__main__':
    app.run(debug=True, port=5001)