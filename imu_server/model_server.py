# model_server.py
from flask import Flask, request, jsonify
from transformers import pipeline
import numpy as np

app = Flask(__name__)

# Initialize pipelines with your specific models
emotion_classifier = pipeline(
    "text-classification", 
    model="j-hartmann/emotion-english-distilroberta-base"
)

summarizer = pipeline(
    "summarization", 
    model="Falconsai/text_summarization"
)

@app.route("/analyze/movement", methods=["POST"])
def analyze_movement():
    data = request.json
    
    # Generate sensor summary text
    sensor_summary = f"""
    Movement patterns show:
    - Average acceleration: X={np.mean(data['acc_x']):.2f}, 
      Y={np.mean(data['acc_y']):.2f}, Z={np.mean(data['acc_z']):.2f}
    - Maximum gyroscope variation: {np.max(data['gyro']):.2f} rad/s
    - Magnetometer stability: {np.std(data['mag']):.2f} μT
    """
    
    # Generate pattern description
    descriptors = []
    if np.mean(data['acc_z']) > 9.5: 
        descriptors.append("stable vertical orientation")
    if np.std(data['gyro']) > 0.5: 
        descriptors.append("frequent rotational adjustments")
    if np.mean(np.abs(data['mag'])) < 30: 
        descriptors.append("consistent magnetic field alignment")
    
    pattern_desc = "Movement patterns indicate " + ", ".join(descriptors) if descriptors else "neutral movement patterns"

    # Create full analysis text
    analysis = f"Movement Profile Analysis:\n{sensor_summary}\nDetected Pattern Characteristics:\n{pattern_desc}"

    return jsonify({
        "technical_summary": sensor_summary,
        "emotional_tone": emotion_classifier(sensor_summary[:512])[0],
        "health_insights": summarizer(analysis[:1024])[0]['summary_text']
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
