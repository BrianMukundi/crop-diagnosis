from flask import Flask, request, render_template
from model.predictor import predict_disease
from PIL import Image
import io
import base64

from flask import send_file
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import tempfile


app = Flask(__name__)

# 🧠 Simple in-memory history storage
diagnosis_history = []

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html', history=diagnosis_history)

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        if 'image' not in request.files:
            return render_template('index.html', prediction="No image part", confidence="N/A", history=diagnosis_history)
        
        image_file = request.files['image']
        if image_file.filename == '':
            return render_template('index.html', prediction="No selected image", confidence="N/A", history=diagnosis_history)

        result = predict_disease(image_file)

        # Convert image to base64 for inline display
        image = Image.open(image_file.stream)
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        encoded_image = base64.b64encode(buffered.getvalue()).decode()

        # Save to history
        diagnosis_history.insert(0, {
            'image': encoded_image,
            'disease': result['disease'],
            'confidence': result['confidence']
        })

        return render_template('index.html', prediction=result['disease'], confidence=result['confidence'], history=diagnosis_history)

    return render_template('index.html', history=diagnosis_history)

if __name__ == '__main__':
    app.run(debug=True)




@app.route('/download-report')
def download_report():
    if not diagnosis_history:
        return "No history available to export."

    # Create a temp file
    temp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    c = canvas.Canvas(temp.name, pagesize=letter)
    width, height = letter
    y = height - 40

    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, y, "Crop Disease Diagnosis Report")
    y -= 30

    c.setFont("Helvetica", 12)
    for idx, item in enumerate(diagnosis_history):
        c.drawString(40, y, f"{idx+1}. Disease: {item['disease']}, Confidence: {item['confidence']}")
        y -= 20
        if y < 50:
            c.showPage()
            y = height - 40
            c.setFont("Helvetica", 12)

    c.save()
    return send_file(temp.name, as_attachment=True, download_name="diagnosis_report.pdf")
