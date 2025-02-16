import json
import numpy as np
import matplotlib.pyplot as plt  # Import matplotlib for plotting
from transformers import pipeline
import torch

# Disable MPS and force CPU
torch.backends.mps.is_available = lambda: False
torch.backends.mps.is_built = lambda: False

class SensorAnalyzer:
    def __init__(self):
        # Initialize the emotion classifier and summarizer on CPU
        self.classifier = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", device="cpu")
        self.summarizer = pipeline("summarization", model="Falconsai/text_summarization", device="cpu")

    def load_data(self, json_file):
        """Load sensor data from a JSON file."""
        data = []
        with open(json_file, 'r') as f:
            for line in f:
                data.append(json.loads(line))
        return data

    def process_data(self, data):
        """Process sensor data into structured format."""
        structured_data = {
            'acc_x': [], 'acc_y': [], 'acc_z': [],
            'gyro_x': [], 'gyro_y': [], 'gyro_z': [],
            'mag_x': [], 'mag_y': [], 'mag_z': [],
            'timestamps': []
        }

        for entry in data:
            if entry['type'] == 'acceleration':
                structured_data['acc_x'].append(entry['data']['x'])
                structured_data['acc_y'].append(entry['data']['y'])
                structured_data['acc_z'].append(entry['data']['z'])
            elif entry['type'] == 'gyroscope':
                structured_data['gyro_x'].append(entry['data']['x'])
                structured_data['gyro_y'].append(entry['data']['y'])
                structured_data['gyro_z'].append(entry['data']['z'])
            elif entry['type'] == 'magnetometer':
                structured_data['mag_x'].append(entry['data']['x'])
                structured_data['mag_y'].append(entry['data']['y'])
                structured_data['mag_z'].append(entry['data']['z'])
            structured_data['timestamps'].append(entry['timestamp'])

        return structured_data

    def analyze_movement_patterns(self, data):
        """Analyze movement patterns and detect specific situations."""
        # Combine gyroscope data for analysis
        gyro_data = data['gyro_x'] + data['gyro_y'] + data['gyro_z']
        
        # Convert sensor data to textual description
        sensor_summary = f"""
        Movement patterns show:
        - Average acceleration: X={np.mean(data['acc_x']):.2f}, Y={np.mean(data['acc_y']):.2f}, Z={np.mean(data['acc_z']):.2f}
        - Maximum gyroscope variation: {np.max(gyro_data):.2f} rad/s
        - Magnetometer stability: {np.std(data['mag_x'] + data['mag_y'] + data['mag_z']):.2f} μT
        """
        
        # Detect specific situations
        situation = self._detect_situation(data)
        
        # Generate emotional tone analysis
        emotion = self.classifier(sensor_summary[:512])[0]
        
        # Create health assessment
        analysis = f"""
        Movement Profile Analysis:
        {sensor_summary}
        
        Detected Situation:
        {situation}
        
        Detected Pattern Characteristics:
        {self._generate_pattern_description(data)}
        """
        
        # Summarize the analysis
        input_text = analysis[:1024]
        summary = self.summarizer(input_text, max_length=50, min_length=10, do_sample=False)[0]['summary_text']

        return {
            "technical_summary": sensor_summary,
            "emotional_tone": emotion,
            "health_insights": summary,
            "detected_situation": situation
        }

    def _detect_situation(self, data):
        """Detect specific situations based on sensor data."""
        # Fall detection: sudden spike in acceleration followed by stillness
        if self._detect_fall(data):
            return "Fall detected: Sudden spike in acceleration followed by stillness."
        
        # Tremor detection: small, rapid oscillations in gyroscope and acceleration data
        if self._detect_tremors(data):
            return "Tremors detected: Small, rapid oscillations in movement data."
        
        # Irregular gait detection: uneven patterns in acceleration and gyroscope data
        if self._detect_irregular_gait(data):
            return "Irregular gait detected: Uneven walking patterns."
        
        return "No specific situation detected."

    def _detect_fall(self, data):
        """Detect a fall based on sudden spike in acceleration and stillness."""
        acc_magnitude = np.sqrt(np.array(data['acc_x'])**2 + np.array(data['acc_y'])**2 + np.array(data['acc_z'])**2)
        
        # Check for sudden spike (fall) followed by stillness
        spike_threshold = 4.0  # Threshold for fall detection
        stillness_threshold = 0.5  # Threshold for stillness
        
        # Detect spike
        if np.max(acc_magnitude) > spike_threshold:
            # Check for stillness after spike
            spike_index = np.argmax(acc_magnitude)
            if spike_index < len(acc_magnitude) - 10:  # Ensure there's enough data after the spike
                post_spike_magnitude = np.mean(acc_magnitude[spike_index + 1:spike_index + 10])
                if post_spike_magnitude < stillness_threshold:
                    return True
        return False

    def _detect_tremors(self, data):
        """Detect tremors based on small, rapid oscillations in gyroscope and acceleration data."""
        # Calculate variance in gyroscope and acceleration data
        gyro_variance = np.var(data['gyro_x'] + data['gyro_y'] + data['gyro_z'])
        acc_variance = np.var(data['acc_x'] + data['acc_y'] + data['acc_z'])
        
        # Tremors are characterized by high variance in small movements
        tremor_threshold = 0.1  # Threshold for tremor detection
        if gyro_variance > tremor_threshold and acc_variance > tremor_threshold:
            return True
        return False

    def _detect_irregular_gait(self, data):
        """Detect irregular gait based on uneven patterns in acceleration and gyroscope data."""
        # Calculate standard deviation of acceleration and gyroscope data
        acc_std = np.std(data['acc_x'] + data['acc_y'] + data['acc_z'])
        gyro_std = np.std(data['gyro_x'] + data['gyro_y'] + data['gyro_z'])
        
        # Irregular gait is characterized by high variability in movement
        irregular_gait_threshold = 0.5  # Threshold for irregular gait detection
        if acc_std > irregular_gait_threshold or gyro_std > irregular_gait_threshold:
            return True
        return False

    def _generate_pattern_description(self, data):
        """Generate natural language description of movement patterns."""
        descriptors = []
        if np.mean(data['acc_z']) > 9.5:
            descriptors.append("stable vertical orientation")
        if np.std(data['gyro_x'] + data['gyro_y'] + data['gyro_z']) > 0.5:
            descriptors.append("frequent rotational adjustments")
        if np.mean(np.abs(data['mag_x'] + data['mag_y'] + data['mag_z'])) < 30:
            descriptors.append("consistent magnetic field alignment")
            
        return "Movement patterns indicate " + ", ".join(descriptors) if descriptors else "neutral movement patterns"

    def generate_report(self, data, output_file="movement_report.txt"):
        """Generate a simple text report with analysis results."""
        analysis = self.analyze_movement_patterns(data)
        
        report = f"""
        Movement Analysis Report
        ========================
        
        Technical Summary:
        {analysis['technical_summary']}
        
        Emotional Tone:
        - Label: {analysis['emotional_tone']['label']}
        - Confidence: {analysis['emotional_tone']['score']:.2f}
        
        Detected Situation:
        {analysis['detected_situation']}
        
        Health Insights:
        {analysis['health_insights']}
        """
        
        with open(output_file, 'w') as f:
            f.write(report)
        print(f"Report generated: {output_file}")

    def plot_sensor_data(self, data, name):
        """Plot sensor data for visualization."""
        plt.figure(figsize=(12, 8))

        min_length = min(len(data['timestamps']), len(data['acc_x']), len(data['acc_y']), len(data['acc_z']),
                  len(data['gyro_x']), len(data['gyro_y']), len(data['gyro_z']),
                  len(data['mag_x']), len(data['mag_y']), len(data['mag_z']))

        # Plot acceleration data
        plt.subplot(3, 1, 1)
        plt.plot(data['timestamps'][:min_length], data['acc_x'][:min_length], label='Acc X')
        plt.plot(data['timestamps'][:min_length], data['acc_y'][:min_length], label='Acc Y')
        plt.plot(data['timestamps'][:min_length], data['acc_z'][:min_length], label='Acc Z')
        plt.title('Acceleration Data Over Time')
        plt.xlabel('Time')
        plt.ylabel('Acceleration (m/s^2)')
        plt.legend()

        # Plot gyroscope data
        plt.subplot(3, 1, 2)
        plt.plot(data['timestamps'][:min_length], data['gyro_x'][:min_length], label='Gyro X')
        plt.plot(data['timestamps'][:min_length], data['gyro_y'][:min_length], label='Gyro Y')
        plt.plot(data['timestamps'][:min_length], data['gyro_z'][:min_length], label='Gyro Z')
        plt.title('Gyroscope Data Over Time')
        plt.xlabel('Time')
        plt.ylabel('Angular Velocity (rad/s)')
        plt.legend()

        # Plot magnetometer data
        plt.subplot(3, 1, 3)
        plt.plot(data['timestamps'][:min_length], data['mag_x'][:min_length], label='Mag X')
        plt.plot(data['timestamps'][:min_length], data['mag_y'][:min_length], label='Mag Y')
        plt.plot(data['timestamps'][:min_length], data['mag_z'][:min_length], label='Mag Z')
        plt.title('Magnetometer Data Over Time')
        plt.xlabel('Time')
        plt.ylabel('Magnetic Field (μT)')
        plt.legend()

        plt.tight_layout()
        plt.savefig(name)
        plt.show()

if __name__ == "__main__":
    # Path to your JSON file
    json_files = ["sensor_metrics.json"]
    
    # Initialize analyzer
    analyzer = SensorAnalyzer()
    
    # Load and process data
    for file in json_files:
        raw_data = analyzer.load_data(file)
        structured_data = analyzer.process_data(raw_data)
        
        # Generate and save report
        output_file_name = "report_" + file[:4] + ".txt"
        analyzer.generate_report(structured_data, output_file_name)
        
        