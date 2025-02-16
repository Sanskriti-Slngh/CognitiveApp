import socket
import time
import json
import struct
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
from transformers import pipeline

import socket
import time
import json
import struct
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
from transformers import pipeline
import torch

class CognitiveAnalyzer:
    """
    A class that analyzes movement patterns from IMU sensor data using transformer models.
    
    This analyzer uses pre-trained transformer models to:
    1. Classify the emotional characteristics of movement patterns
    2. Generate natural language summaries of movement data
    3. Provide health-related insights based on movement patterns
    
    The class ensures all computations happen on CPU to avoid device-related issues.
    """
    
    def __init__(self):
        """
        Initialize the CognitiveAnalyzer with required ML models.
        Forces CPU usage for all models to prevent GPU/MPS-related errors.
        """
        # Force CPU for all models to avoid MPS/GPU issues
        self.device = "cpu"
        
        # Initialize emotion classification model
        self.classifier = pipeline(
            "text-classification",
            model="j-hartmann/emotion-english-distilroberta-base",
            device=self.device
        )
        
        # Initialize text summarization model
        self.summarizer = pipeline(
            "summarization",
            model="Falconsai/text_summarization",
            device=self.device
        )

    def analyze_movement_patterns(self, data):
        """
        Analyze movement patterns from sensor data and generate insights.
        
        Args:
            data (dict): Dictionary containing sensor data with keys:
                'acc_x', 'acc_y', 'acc_z' - Acceleration data
                'gyro_x', 'gyro_y', 'gyro_z' - Gyroscope data
                'mag_x', 'mag_y', 'mag_z' - Magnetometer data
        
        Returns:
            dict: Analysis results containing:
                'technical_summary': Raw sensor data analysis
                'emotional_tone': Detected movement characteristics
                'health_insights': Summarized health-related observations
        """
        # Combine gyroscope data for comprehensive rotation analysis
        gyro_data = np.array(data['gyro_x']) + np.array(data['gyro_y']) + np.array(data['gyro_z'])
        
        # Generate technical summary of sensor readings
        sensor_summary = f"""
        Movement patterns show:
        - Average acceleration: X={np.mean(data['acc_x']):.2f}, Y={np.mean(data['acc_y']):.2f}, Z={np.mean(data['acc_z']):.2f}
        - Maximum gyroscope variation: {np.max(gyro_data):.2f} rad/s
        - Magnetometer stability: {np.std(np.array(data['mag_x']) + np.array(data['mag_y']) + np.array(data['mag_z'])):.2f} μT
        """
        
        # Generate pattern description and combine with sensor summary
        analysis = f"""
        Movement Profile Analysis:
        {sensor_summary}
        
        Detected Pattern Characteristics:
        {self._generate_pattern_description(data)}
        """
        
        # Classify emotional characteristics of movement
        emotion = self.classifier(sensor_summary[:512])[0]
        
        # Generate condensed summary of the analysis
        # Limit input length to 1024 tokens to prevent overflow
        summary = self.summarizer(
            analysis[:1024],
            max_length=40,
            min_length=20,
            do_sample=False,
            clean_up_tokenization_spaces=True
        )[0]['summary_text']
        
        return {
            "technical_summary": sensor_summary,
            "emotional_tone": emotion,
            "health_insights": summary
        }
    
    def _generate_pattern_description(self, data):
        """
        Generate natural language description of movement patterns.
        
        Args:
            data (dict): Dictionary containing sensor data
            
        Returns:
            str: Natural language description of movement patterns
        """
        descriptors = []
        
        # Check for stable vertical orientation
        # Normal gravity is ~9.81 m/s², so >9.5 indicates mostly vertical
        if np.mean(data['acc_z']) > 9.5:
            descriptors.append("stable vertical orientation")
            
        # Check for significant rotational movement
        # Standard deviation >0.5 rad/s indicates frequent rotation
        if np.std(np.array(data['gyro_x']) + np.array(data['gyro_y']) + np.array(data['gyro_z'])) > 0.5:
            descriptors.append("frequent rotational adjustments")
            
        # Check for magnetic field alignment
        # Low magnetic field variation indicates consistent orientation
        if np.mean(np.abs(np.array(data['mag_x']) + np.array(data['mag_y']) + np.array(data['mag_z']))) < 30:
            descriptors.append("consistent magnetic field alignment")
        
        # Combine descriptors into natural language
        return "Movement patterns indicate " + ", ".join(descriptors) if descriptors else "neutral movement patterns"
class MovementVisualizer:
    def generate_movement_plots(self, data):
        if not data['timestamps'] or not data['acc_x']:
            print("No data available for plotting.")
            return
        """Generate professional visualization plots"""
        plt.figure(figsize=(12, 8))
        
        # Time series plot
        plt.subplot(2, 2, 1)
        plt.plot(data['timestamps'], data['acc_x'], label='X')
        plt.plot(data['timestamps'], data['acc_y'], label='Y')
        plt.plot(data['timestamps'], data['acc_z'], label='Z')
        plt.title('Acceleration Over Time')
        plt.ylabel('m/s²')
        plt.legend()
        
        # Gyroscope heatmap
        plt.subplot(2, 2, 2)
        plt.hist2d(data['gyro_x'], data['gyro_y'], bins=20, cmap='viridis')
        plt.colorbar(label='Frequency')
        plt.title('Rotational Movement Distribution')
        plt.xlabel('X-axis rotation')
        plt.ylabel('Y-axis rotation')
        
        # Save plots
        plt.tight_layout()
        plt.savefig('movement_analysis.png')
        plt.close()


class IMU_Server:
    REQUEST_SIZE = 4
    RESPONSE_PAYLOAD_SIZE = 12

    REQ_READ_ACCELERATION = 0x51
    REQ_READ_GYROSCOPE    = 0x52
    REQ_READ_MAGNETOMETER = 0x53
    REQ_START_LED_GAME    = 0x54

    def __init__(self, host='0.0.0.0', port=20905):
        self.host = host
        self.port = port
        self.client_socket = None
        self.client_address = None
        self.log_file = "sensor_metrics.json"  # File to store metrics
        self.analyzer = CognitiveAnalyzer()
        self.visualizer = MovementVisualizer()
        self.full_dataset = {
            'acc_x': [], 'acc_y': [], 'acc_z': [],
            'gyro_x': [], 'gyro_y': [], 'gyro_z': [],
            'mag_x': [], 'mag_y': [], 'mag_z': [],
            'timestamps': [],
            'reaction_times': []
        }           
        self.last_accel_x = 0.0
        self.last_accel_y = 0.0
        self.last_accel_z = 0.0
        self.last_gyro_x = 0.0
        self.last_gyro_y = 0.0
        self.last_gyro_z = 0.0
        self.last_mag_x = 0.0
        self.last_mag_y = 0.0
        self.last_mag_z = 0.0
    def _generate_report(self):
        """Generate comprehensive HTML report with AI insights"""
        technical_metrics = self._calculate_technical_metrics()
        cognitive_analysis = self.analyzer.analyze_movement_patterns(self.full_dataset)
        
        # Generate a technical summary string
        technical_summary = f"""
        Analysis of movement patterns over {len(self.full_dataset['timestamps'])} samples:
        - Stability Index: {technical_metrics['stability']:.2f}/100
        - Movement Efficiency: {technical_metrics['efficiency']:.2f}/100
        - Average Acceleration: X={np.mean(self.full_dataset['acc_x']):.2f}, 
                            Y={np.mean(self.full_dataset['acc_y']):.2f}, 
                            Z={np.mean(self.full_dataset['acc_z']):.2f} m/s²
        """
        
        report_data = {
            "technical": {
                "metrics": technical_metrics,
                "summary": technical_summary
            },
            "cognitive": cognitive_analysis,
            "visualization": 'movement_analysis.png'
        }
        
        # Generate HTML report
        html_report = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    h1, h2 {{ color: #333; }}
                    .metrics {{ 
                        background-color: #f5f5f5;
                        padding: 20px;
                        border-radius: 5px;
                        margin: 20px 0;
                    }}
                </style>
            </head>
            <body>
                <h1>Movement Analysis Report</h1>
                
                <h2>Technical Summary</h2>
                <div class="metrics">
                    <pre>{report_data['technical']['summary']}</pre>
                </div>
                
                <h2>Cognitive Insights</h2>
                <p>{report_data['cognitive']['health_insights']}</p>
                <p>Emotional Tone: {report_data['cognitive']['emotional_tone']['label']} 
                (confidence: {report_data['cognitive']['emotional_tone']['score']:.2f})</p>
                
                <h2>Movement Visualization</h2>
                <img src="{report_data['visualization']}" width="100%">
                
                <h3>Detailed Metrics</h3>
                <div class="metrics">
                    <ul>
                        <li>Stability Index: {report_data['technical']['metrics']['stability']:.2f}/100</li>
                        <li>Movement Efficiency: {report_data['technical']['metrics']['efficiency']:.2f}/100</li>
                    </ul>
                </div>
            </body>
        </html>
        """
        
        with open('movement_report.html', 'w') as f:
            f.write(html_report)
        
        return html_report

    def _calculate_technical_metrics(self):
        """Calculate advanced movement metrics."""
        return {
            'stability': self._calculate_stability_index(),
            'efficiency': self._calculate_movement_efficiency(),
            'reaction': 0.0  # Placeholder, since reaction_times is not defined
        }
    def _calculate_stability_index(self):
        """Calculate stability index based on acceleration variance."""
        if not self.full_dataset['acc_x']:
            return 0.0  # No data available
        
        # Calculate variance for each axis
        var_x = np.var(self.full_dataset['acc_x'])
        var_y = np.var(self.full_dataset['acc_y'])
        var_z = np.var(self.full_dataset['acc_z'])
        
        # Average variance across all axes
        avg_variance = (var_x + var_y + var_z) / 3
        
        # Stability index: 100 = perfectly stable, 0 = highly unstable
        stability_index = max(0, 100 - (avg_variance * 10))  # Scale variance to 0-100 range
        return stability_index
    def _calculate_movement_efficiency(self):
        """Calculate movement efficiency based on gyroscope smoothness."""
        if not self.full_dataset['gyro_x']:
            return 0.0  # No data available
        
        # Calculate jerk (rate of change of angular velocity)
        jerk_x = np.diff(self.full_dataset['gyro_x'])
        jerk_y = np.diff(self.full_dataset['gyro_y'])
        jerk_z = np.diff(self.full_dataset['gyro_z'])
        
        # Average jerk magnitude across all axes
        avg_jerk = (np.mean(np.abs(jerk_x)) + np.mean(np.abs(jerk_y)) + np.mean(np.abs(jerk_z))) / 3
        
        # Movement efficiency: 100 = perfectly efficient, 0 = highly inefficient
        efficiency = max(0, 100 - (avg_jerk * 20))  # Scale jerk to 0-100 range
        return efficiency

    def start(self):
        # Initialize the server socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(1)
        print(f"IMU Server listening on {self.host}:{self.port}")

        # Accept a client connection
        self.client_socket, self.client_address = self.server_socket.accept()
        print(f"Client connected from {self.client_address}")

        # Initialize variables for data collection
        start_time = time.time()
        led_game_counter = 0  # To trigger LED game every 10 cycles

        # Collect data for 30 seconds
        while (time.time() - start_time) < 30:
            if not self.client_socket:
                self.start()  # Reconnect if client disconnects
            
            # Send sensor requests and collect data
            self.send_request(self.REQ_READ_ACCELERATION)
            self.receive_response()
            self.send_request(self.REQ_READ_GYROSCOPE)
            self.receive_response()
            self.send_request(self.REQ_READ_MAGNETOMETER)
            self.receive_response()

            # Store data in full_dataset
            self.full_dataset['timestamps'].append(time.time() - start_time)
            self.full_dataset['acc_x'].append(self.last_accel_x)
            self.full_dataset['acc_y'].append(self.last_accel_y)
            self.full_dataset['acc_z'].append(self.last_accel_z)
            self.full_dataset['gyro_x'].append(self.last_gyro_x)
            self.full_dataset['gyro_y'].append(self.last_gyro_y)
            self.full_dataset['gyro_z'].append(self.last_gyro_z)
            self.full_dataset['mag_x'].append(self.last_mag_x)
            self.full_dataset['mag_y'].append(self.last_mag_y)
            self.full_dataset['mag_z'].append(self.last_mag_z)

            # Send LED game request every 10 cycles (~1 second delay * 10)
            led_game_counter += 1
            if led_game_counter >= 10:
                self.send_request(self.REQ_START_LED_GAME)
                self.receive_response()
                led_game_counter = 0

            # Debug prints to verify data collection
            print(f"Timestamps: {len(self.full_dataset['timestamps'])}, "
                f"Acc X: {len(self.full_dataset['acc_x'])}, "
                f"Gyro X: {len(self.full_dataset['gyro_x'])}, "
                f"Mag X: {len(self.full_dataset['mag_x'])}")

            time.sleep(0.1)  # 100ms delay between readings

        # After 30 seconds, generate plots and report
        if self.full_dataset['timestamps']:  # Ensure data was collected
            self.visualizer.generate_movement_plots(self.full_dataset)
            report = self._generate_report()
            print(f"Report generated: movement_report.html")
        else:
            print("No data collected. Skipping report generation.")

        # Close the client socket
        if self.client_socket:
            self.client_socket.close()
            self.client_socket = None
            self.client_address = None
            
    def _log_data(self, data):
        """Append data to the log file in JSON format."""
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(data) + '\n')

    def processAcceleration(self, x, y, z):
        # Store values
        self.last_accel_x = x
        self.last_accel_y = y
        self.last_accel_z = z
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "acceleration",
            "data": {"x": x, "y": y, "z": z}
        }
        self._log_data(log_entry)
        print(f"Acceleration: {x:.2f}, {y:.2f}, {z:.2f}")

    def processGyroscope(self, x, y, z):
        # Store values
        self.last_gyro_x = x
        self.last_gyro_y = y
        self.last_gyro_z = z
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "gyroscope",
            "data": {"x": x, "y": y, "z": z}
        }
        self._log_data(log_entry)
        print(f"Gyroscope: {x:.2f}, {y:.2f}, {z:.2f}")

    def processMagnetometer(self, x, y, z):
        # Store values
        self.last_mag_x = x
        self.last_mag_y = y
        self.last_mag_z = z
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "magnetometer",
            "data": {"x": x, "y": y, "z": z}
        }
        self._log_data(log_entry)
        print(f"Magnetometer: {x:.2f}, {y:.2f}, {z:.2f}")

    def processLEDGame(self, red_on, red_success, green_on, green_success, blue_on, blue_success):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "led_game",
            "data": {
                "red": {"on": red_on, "success": red_success},
                "green": {"on": green_on, "success": green_success},
                "blue": {"on": blue_on, "success": blue_success}
            }
        }
        self._log_data(log_entry)
        print(f"LED Game Results - Red: {red_on}/{red_success}, Green: {green_on}/{green_success}, Blue: {blue_on}/{blue_success}")

    def send_request(self, request_type):
        if not self.client_socket:
            return

        try:
            req_payload = bytes([0x01, 0x02, 0x03])  # Unused payload
            request = struct.pack('<B3s', request_type, req_payload)
            self.client_socket.send(request)
        except Exception as e:
            print(f"Error sending request: {e}")
            self.handle_disconnection()

    def receive_response(self):
        if not self.client_socket:
            return

        try:
            resp_type_arr = self.client_socket.recv(1)
            if not resp_type_arr:
                return
            resp_type = resp_type_arr[0]
            reserved_data = self.client_socket.recv(3)  # Ignore reserved

            payload = self.client_socket.recv(self.RESPONSE_PAYLOAD_SIZE)
            if len(payload) != self.RESPONSE_PAYLOAD_SIZE:
                return

            if resp_type == self.REQ_READ_ACCELERATION:
                x, y, z = struct.unpack('<fff', payload)
                self.processAcceleration(x, y, z)

            elif resp_type == self.REQ_READ_GYROSCOPE:
                x, y, z = struct.unpack('<fff', payload)
                self.processGyroscope(x, y, z)

            elif resp_type == self.REQ_READ_MAGNETOMETER:
                x, y, z = struct.unpack('<fff', payload)
                self.processMagnetometer(x, y, z)

            elif resp_type == self.REQ_START_LED_GAME:
                # Unpack 6 unsigned shorts (H) from payload
                data = struct.unpack('<6H', payload)
                self.processLEDGame(data[0], data[1], data[2], data[3], data[4], data[5])

        except Exception as e:
            print(f"Error receiving response: {e}")
            self.handle_disconnection()

    def handle_disconnection(self):
        print("Client disconnected. Waiting for reconnection...")
        if self.client_socket:
            self.client_socket.close()
            self.client_socket = None
            self.client_address = None

if __name__ == "__main__":
    server = IMU_Server()
    server.start()
