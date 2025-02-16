
## Install Dependencies:

This repository contains a web application for analyzing cognitive health using multiple modalities including speech, movement (IMU sensor data), and interactive cognitive games. The app is built with [Streamlit](https://streamlit.io/) and includes data analysis using machine learning pipelines, sensor data visualization, and a performance tracker for cognitive games.

## Repository Structure

├── analyze_sensor_data.py    # Module for processing and analyzing sensor data.

├── cognitive_files.html      # HTML file for the cognitive games interface.

├── demo.py                   # Main Streamlit application file.

├── diagnostic_model.py       # Module for generating diagnostic insights from speech features.

├── feature_extractor.py      # Module for extracting speech features.

├── index.html                # Standalone HTML page (optional).

├── sensor_metrics.json       # Sample sensor metrics data in JSON format.

├── static                    # Folder containing static assets.

│   ├── script.js             # JavaScript for cognitive games.

│   └── style.css             # CSS styling for cognitive games.

└── README.md                 # This file.

## Features

- **Voice Analysis:**  
  Analyze speech features (e.g., voice stability, pause count, frequency, etc.) and generate advanced neural metrics and clinical insights.

- **Movement Analysis:**  
  Real-time IMU sensor data collection and visualization including movement stability and smoothness metrics.

- **Sensor Data Analysis Report:**  
  Process static sensor data from JSON, visualize technical summaries and structured sensor data, and highlight detected situations with visual components.

- **Cognitive Games & Performance Tracker:**  
  Play cognitive games and track user performance across multiple games.

## Setup and Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/your-username/your-repository.git
   cd your-repository
   ```

2. **Install Dependencies:**

   Ensure you have Python 3.7 or later installed. Install the required packages using pip:

   ```bash
   pip install streamlit plotly transformers torch numpy
   ```

   Optionally, if you plan to expose the app publicly (e.g., running in Google Colab), install [pyngrok](https://pypi.org/project/pyngrok/):

   ```bash
   pip install pyngrok
   ```

3. **(Optional) Set Up Ngrok:**

   If you wish to expose the app publicly, configure Ngrok by obtaining a token from [ngrok.com](https://ngrok.com/) and following their documentation.

## Running the Application

### Running the Streamlit App

To start the main application, run:

```bash
streamlit run demo.py
```

This command launches the Streamlit app locally (by default on port `8501`). To expose it publicly using Ngrok, you can use the following snippet:

```python
from pyngrok import ngrok
import os

# Run Streamlit in the background
os.system("streamlit run demo.py &")

# Connect Ngrok tunnel to the default Streamlit port (8501)
public_url = ngrok.connect(8501)
print("Streamlit Public URL:", public_url)
```

### Running the Cognitive Games (Optional)

The cognitive games interface is integrated into the Streamlit app in the "Cognitive Games" tab. If you prefer to run a standalone version (e.g., using `index.html`), you can serve it using Python's HTTP server:

```bash
python -m http.server 8000
```

Then navigate to `http://localhost:8000` in your browser.

## File Descriptions

- **analyze_sensor_data.py:**  
  Contains the `SensorAnalyzer` class for processing raw sensor data, generating technical summaries, performing emotion analysis, detecting movement situations (e.g., tremors, falls), and visualizing sensor data.

- **diagnostic_model.py:**  
  Implements a diagnostic model that uses extracted speech features to generate clinical insights and risk assessments.

- **feature_extractor.py:**  
  Extracts various features from a provided audio file for voice analysis.

- **demo.py:**  
  The main Streamlit application that integrates voice analysis, movement analysis, sensor data reports, and cognitive games into a unified web interface.

- **sensor_metrics.json:**  
  A sample JSON file containing sensor metrics data used for sensor data analysis.

- **static/**  
  Contains static assets (CSS and JS) used by the cognitive games interface.

- **cognitive_files.html:**  
  HTML for the cognitive games interface that is inlined within the Streamlit app.

- **index.html:**  
  A standalone HTML page (if needed) for displaying the cognitive games interface.

## Troubleshooting

- **Ngrok Issues:**  
  If you experience issues with Ngrok (e.g., `ERR_NGROK_3200`), ensure that your Ngrok token is properly configured and that no conflicting tunnels are active.

- **Localhost Conflicts:**  
  If you receive errors regarding ports already in use, ensure that no other applications are running on the specified ports (`8501` for Streamlit and `8000` for the HTTP server).

## Contact

For any questions or feedback, please open an issue or contact [ssingh7@mit.edu](mailto:ssingh7@mit.edu).
