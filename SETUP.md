# Flask Backend Setup Guide

## How to Run

### Step 1: Install Dependencies
Open PowerShell in your project folder and run:
```powershell
pip install -r requirements.txt
```

### Step 2: Start the Flask Server
```powershell
python app.py
```

You should see output like:
```
 * Running on http://localhost:5000
```

### Step 3: Open the Web Application
Open your web browser and go to:
```
file:///c:/Users/vikin/Documents/EtownMotionTracking/Recording_Page2.html
```

Or use a local web server (recommended):
```powershell
python -m http.server 8000
```
Then visit: `http://localhost:8000/Recording_Page2.html`

### Step 4: Use the Application
1. Click the "Run Python" button to start recording
2. The Flask server will capture video from your webcam
3. Pose landmarks will be detected and displayed
4. Click "Stop Recording" to end the session
5. The recorded video will be saved as `camera_recording.avi`

## How It Works

- **app.py**: Flask backend that handles:
  - Webcam video capture
  - Pose detection using MediaPipe
  - Frame streaming to the browser
  - Video file saving
  
- **Recording_Page2.html**: Web frontend that:
  - Displays live video feed
  - Shows pose landmarks
  - Controls recording start/stop

## Troubleshooting

**"Cannot connect to Flask server" error:**
- Make sure Flask is running on port 5000
- Check that no other application is using port 5000
- Try restarting the Flask server

**"Cannot open webcam" error:**
- Make sure your webcam is connected
- Check that no other application is using the webcam
- Try restarting your computer

**Model file not found:**
- Make sure `pose_landmarker_full.task` is in your project folder
- Download it from: https://ai.google.dev/edge/mediapipe/solutions/vision/pose_landmarker
