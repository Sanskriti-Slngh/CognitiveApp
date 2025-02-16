import numpy as np
import socket
import threading
import time
import json
import struct
import os
from queue import Queue

import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from feature_extractor import SpeechFeatureExtractor
from diagnostic_model import DiagnosticModel
from analyze_sensor_data import SensorAnalyzer  # Import the analyzer class

# Global queue for IMU data sharing
imu_data_queue = Queue()

# -------------------- IMU Data Processor --------------------
class IMUDataProcessor:
    def __init__(self):
        self.acceleration_data = []
        self.gyroscope_data = []
        self.magnetometer_data = []
        
    def update_data(self, data_type, x, y, z):
        if data_type == "acceleration":
            self.acceleration_data.append({"x": x, "y": y, "z": z})
            if len(self.acceleration_data) > 100:
                self.acceleration_data.pop(0)
        elif data_type == "gyroscope":
            self.gyroscope_data.append({"x": x, "y": y, "z": z})
            if len(self.gyroscope_data) > 100:
                self.gyroscope_data.pop(0)
        elif data_type == "magnetometer":
            self.magnetometer_data.append({"x": x, "y": y, "z": z})
            if len(self.magnetometer_data) > 100:
                self.magnetometer_data.pop(0)

# -------------------- Voice Analysis Helpers --------------------
def calculate_cognitive_score(features):
    weights = {
        'voice_stability': 0.2,
        'pause_count': -0.15,
        'mean_pause_duration': -0.15,
        'theta_power': -0.25,
        'beta_power': 0.25
    }
    total = sum(weights[k] * features[k] for k in weights if k in features)
    return min(99.99, max(0.01, 50 + total * 10))

def format_metric(value):
    return f"{value:.2f}"

def display_advanced_health_assessment(features):
    st.subheader("🧠 Advanced Health Assessment")
    
    cognitive_score = calculate_cognitive_score(features)
    processing_score = 100 - (features['mean_pause_duration'] * 20)
    attention_score = 100 - (features['theta_power'] * 2)
    memory_score = features['beta_power'] * 10

    st.markdown("#### Detailed Neural Metrics")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Voice Stability", f"{features['voice_stability']*100:.2f}%")
    with c2:
        st.metric("Attention Index", f"{attention_score:.2f}%")
    with c3:
        st.metric("Memory Score", f"{memory_score:.2f}%")
    
    st.markdown("#### 🔍 Risk Analysis")
    rc1, rc2 = st.columns(2)
    with rc1:
        risk_score = 100 - cognitive_score
        st.metric("Cognitive Decline Risk", f"{risk_score:.2f}%", delta=f"{cognitive_score - 50:+.2f}% from baseline", delta_color="inverse")
    with rc2:
        proc_risk = 100 - processing_score
        st.metric("Processing Speed Risk", f"{proc_risk:.2f}%", delta=f"{processing_score - 50:+.2f}% from baseline", delta_color="inverse")
    
    # Radar chart visualization
    categories = ['Attention', 'Memory', 'Language', 'Processing', 'Stability']
    values = [
        attention_score,
        memory_score,
        cognitive_score,
        processing_score,
        features['voice_stability'] * 100
    ]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=values, theta=categories, fill='toself', name="Neural Metrics"))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# -------------------- IMU & Movement Analysis --------------------
def calculate_stability(data):
    if not data:
        return 100.0
    x = [d['x'] for d in data]
    y = [d['y'] for d in data]
    z = [d['z'] for d in data]
    var_avg = np.mean([np.var(x), np.var(y), np.var(z)])
    return max(0, min(100, 100 * (1 - var_avg)))

def calculate_smoothness(data):
    if not data:
        return 0.0
    x = [d['x'] for d in data]
    y = [d['y'] for d in data]
    z = [d['z'] for d in data]
    jerk_x = np.diff(x, 2) if len(x) > 2 else [0]
    jerk_y = np.diff(y, 2) if len(y) > 2 else [0]
    jerk_z = np.diff(z, 2) if len(z) > 2 else [0]
    jerk_score = np.mean([np.mean(np.abs(jerk_x)), np.mean(np.abs(jerk_y)), np.mean(np.abs(jerk_z))])
    return max(0, min(100, 100 * (1 - jerk_score)))

def display_imu_data(imu_processor):
    st.subheader("🔄 Real-time Movement Analysis")
    
    while not imu_data_queue.empty():
        try:
            pkt = imu_data_queue.get_nowait()
            imu_processor.update_data("acceleration", pkt["acceleration"]["x"], pkt["acceleration"]["y"], pkt["acceleration"]["z"])
            imu_processor.update_data("gyroscope", pkt["gyroscope"]["x"], pkt["gyroscope"]["y"], pkt["gyroscope"]["z"])
            imu_processor.update_data("magnetometer", pkt["magnetometer"]["x"], pkt["magnetometer"]["y"], pkt["magnetometer"]["z"])
        except Exception as e:
            st.write("Error processing IMU data:", e)

    c1, c2 = st.columns(2)
    with c1:
        st.metric("Movement Stability", f"{calculate_stability(imu_processor.acceleration_data):.2f}%")
    with c2:
        st.metric("Movement Smoothness", f"{calculate_smoothness(imu_processor.gyroscope_data):.2f}%")
    
    if imu_processor.acceleration_data:
        times = list(range(len(imu_processor.acceleration_data)))
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=times, y=[d['x'] for d in imu_processor.acceleration_data],
                                 name='X-axis', line=dict(color='#4281A4')))
        fig.add_trace(go.Scatter(x=times, y=[d['y'] for d in imu_processor.acceleration_data],
                                 name='Y-axis', line=dict(color='#48A9A6')))
        fig.add_trace(go.Scatter(x=times, y=[d['z'] for d in imu_processor.acceleration_data],
                                 name='Z-axis', line=dict(color='#C1666B')))
        fig.update_layout(title="Movement Patterns Over Time",
                          xaxis_title="Time", yaxis_title="Acceleration", height=400)
        st.plotly_chart(fig, use_container_width=True)

def imu_collection():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('localhost', 20906))
        s.listen(1)
        conn, addr = s.accept()
        while True:
            data = conn.recv(1024)
            if not data:
                break
            pkt = json.loads(data.decode())
            imu_data_queue.put(pkt)
    except Exception as e:
        print(f"IMU server error: {e}")
    finally:
        s.close()

# -------------------- Helper: Plot Structured Sensor Data --------------------
def plot_structured_sensor_data(structured_data):
    """
    Create a 3-row subplot:
      Row 1: Acceleration (acc_x, acc_y, acc_z)
      Row 2: Gyroscope (gyro_x, gyro_y, gyro_z)
      Row 3: Magnetometer (mag_x, mag_y, mag_z)
    """
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                        subplot_titles=("Acceleration", "Gyroscope", "Magnetometer"))
    
    timestamps = structured_data['timestamps']
    
    # Acceleration data
    fig.add_trace(go.Scatter(x=timestamps, y=structured_data['acc_x'], mode="lines", name="Acc X",
                             line=dict(color='#4281A4')), row=1, col=1)
    fig.add_trace(go.Scatter(x=timestamps, y=structured_data['acc_y'], mode="lines", name="Acc Y",
                             line=dict(color='#48A9A6')), row=1, col=1)
    fig.add_trace(go.Scatter(x=timestamps, y=structured_data['acc_z'], mode="lines", name="Acc Z",
                             line=dict(color='#C1666B')), row=1, col=1)
    
    # Gyroscope data
    fig.add_trace(go.Scatter(x=timestamps, y=structured_data['gyro_x'], mode="lines", name="Gyro X",
                             line=dict(color='#4281A4')), row=2, col=1)
    fig.add_trace(go.Scatter(x=timestamps, y=structured_data['gyro_y'], mode="lines", name="Gyro Y",
                             line=dict(color='#48A9A6')), row=2, col=1)
    fig.add_trace(go.Scatter(x=timestamps, y=structured_data['gyro_z'], mode="lines", name="Gyro Z",
                             line=dict(color='#C1666B')), row=2, col=1)
    
    # Magnetometer data
    fig.add_trace(go.Scatter(x=timestamps, y=structured_data['mag_x'], mode="lines", name="Mag X",
                             line=dict(color='#4281A4')), row=3, col=1)
    fig.add_trace(go.Scatter(x=timestamps, y=structured_data['mag_y'], mode="lines", name="Mag Y",
                             line=dict(color='#48A9A6')), row=3, col=1)
    fig.add_trace(go.Scatter(x=timestamps, y=structured_data['mag_z'], mode="lines", name="Mag Z",
                             line=dict(color='#C1666B')), row=3, col=1)
    
    fig.update_layout(height=800, title_text="Structured Sensor Data Visualization")
    return fig

# -------------------- MAIN APP --------------------
def main():
    st.title("🧠 Cognitive Health Analyzer")

    # Create three tabs: Voice Analysis, Movement Analysis, Cognitive Games
    tab1, tab2, tab3 = st.tabs(["Voice Analysis", "Movement Analysis", "Cognitive Games"])

    if 'imu_processor' not in st.session_state:
        st.session_state.imu_processor = IMUDataProcessor()

    # --- Tab 1: Voice Analysis ---
    with tab1:
        if st.button("Generate Voice Analysis"):
            with st.spinner("Analyzing speech patterns..."):
                extractor = SpeechFeatureExtractor()
                features = extractor.extract_features("synthetic_audio.wav")
                
                st.subheader("🎤 Speech Features")
                fc1, fc2, fc3 = st.columns(3)
                with fc1:
                    st.metric("Voice Stability", f"{features['voice_stability']*100:.2f}%")
                    st.metric("Mean F0", f"{features['mean_f0']:.2f}")
                with fc2:
                    st.metric("Pause Count", f"{features['pause_count']:.2f}")
                    st.metric("Mean Pause Duration", f"{features['mean_pause_duration']:.2f}")
                with fc3:
                    st.metric("Theta Power", f"{features['theta_power']:.2f}")
                    st.metric("Beta Power", f"{features['beta_power']:.2f}")

                display_advanced_health_assessment(features)

                model = DiagnosticModel()
                diag = model.diagnose(features)
                st.subheader("📋 Clinical Insights")
                for k, v in diag['risk_indicators'].items():
                    st.markdown(f"**{k.replace('_',' ').title()}**")
                    st.write(f"Value: {v['value']:.2f}")
                    st.write(f"Threshold: {v['threshold']}")
                    st.write(f"Clinical Significance: {v['clinical_significance']}")
    
    # --- Tab 2: Movement Analysis ---
    with tab2:
        if "collection_started" not in st.session_state:
            st.session_state.collection_started = False
        if st.button("Start Movement Analysis") or st.session_state.collection_started:
            if not st.session_state.collection_started:
                thread = threading.Thread(target=imu_collection, daemon=True)
                thread.start()
                st.session_state.collection_started = True
                st.write("IMU data collection started...")
            display_imu_data(st.session_state.imu_processor)

        st.markdown("---")
        st.subheader("Sensor Data Analysis Report")
        if st.button("Run Sensor Data Analysis Report"):
            analyzer_sensor = SensorAnalyzer()
            raw_data = analyzer_sensor.load_data("sensor_metrics.json")
            structured_data = analyzer_sensor.process_data(raw_data)
            analysis_result = analyzer_sensor.analyze_movement_patterns(structured_data)
            
            st.markdown("### Technical Summary")
            st.text(analysis_result["technical_summary"])
            
            st.markdown("### Emotional Tone")
            st.json(analysis_result["emotional_tone"])
            
            st.markdown("### Health Insights")
            st.text(analysis_result["health_insights"])
            
            # Display Detected Situation in a highlighted box
            st.markdown("### Detected Situation")
            detected_html = f"""
            <div style="background-color: #ffcccc; border: 2px solid #ff0000; border-radius: 5px; padding: 10px;">
                <strong>{analysis_result["detected_situation"]}</strong>
            </div>
            """
            st.markdown(detected_html, unsafe_allow_html=True)
            
            # New: Display visualizations based on the structured sensor data
            st.markdown("### Structured Sensor Data Visualization")
            fig_sensor = plot_structured_sensor_data(structured_data)
            st.plotly_chart(fig_sensor, use_container_width=True)

    # --- Tab 3: Cognitive Games ---
    with tab3:
        st.subheader("Cognitive Games")
        st.write("Play memory, reaction, and other games to test your cognition!")
        
        # ---------------- Performance Tracker Component ----------------
        st.markdown("## Performance Tracker")
        if "game_scores" not in st.session_state:
            st.session_state.game_scores = {}  # dictionary: {game_name: [score, score, ...]}
        
        with st.form("score_form", clear_on_submit=True):
            game_name = st.text_input("Game Name")
            score = st.number_input("Score", min_value=0.0, max_value=100.0, step=1.0)
            submitted = st.form_submit_button("Submit Score")
            if submitted:
                if game_name.strip() != "":
                    if game_name not in st.session_state.game_scores:
                        st.session_state.game_scores[game_name] = []
                    st.session_state.game_scores[game_name].append(score)
                    st.success(f"Score {score} added for {game_name}!")
                else:
                    st.error("Please enter a game name.")

        st.markdown("### Performance Summary")
        if st.session_state.game_scores:
            performance_data = []
            for game, scores in st.session_state.game_scores.items():
                avg_score = sum(scores) / len(scores)
                performance_data.append({"Game": game, "Average Score": avg_score, "Attempts": len(scores)})
            st.table(performance_data)
        else:
            st.write("No scores submitted yet.")

        # ---------------- Inline Cognitive Games ----------------
        try:
            with open("static/style.css", "r", encoding="utf-8") as fcss:
                style_css = fcss.read()
            with open("static/script.js", "r", encoding="utf-8") as fjs:
                script_js = fjs.read()
            with open("cognitive_games.html", "r", encoding="utf-8") as fhtml:
                cg_html = fhtml.read()
            final_html = f"""
            <style>{style_css}</style>
            {cg_html}
            <script>
            {script_js}
            </script>
            """
            components.html(final_html, height=1000, scrolling=True)
        except Exception as e:
            st.error(f"Error loading cognitive games: {e}")

if __name__ == "__main__":
    main()
