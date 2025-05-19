
from PIL import Image
import io

def predict_disease(image_file):
    image = Image.open(image_file.stream)
    # Replace this with actual model logic later
    return {
        "disease": "Tomato___Late_blight",
        "confidence": "92.3%"
    }
