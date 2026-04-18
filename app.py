from flask import Flask, Response, jsonify, request, send_from_directory
import cv2
import mediapipe as mp
import base64
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
import os
import time
import sqlite3

app = Flask(__name__, static_folder='.', static_url_path='')

# Global variables
camera = None
pose_landmarker = None
latest_frame = None
latest_landmarks = None
recording = False
out = None
video_writer_fps = None
video_writer_size = None
frame_counter = 0  # Counter for skipping pose detection
frame_times = []  # For measuring actual FPS

# MediaPipe pose connections (33-landmark model)
POSE_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 7), (0, 4), (4, 5), (5, 6),  # Head
    (9, 10),  # Torso center
    (11, 12), (11, 13), (13, 15), (12, 14), (14, 16),  # Upper body
    (11, 23), (12, 24),  # Torso to legs
    (15, 17), (17, 19), (19, 21), (15, 21),  # Left arm
    (16, 18), (18, 20), (20, 22), (16, 22),  # Right arm
    (23, 25), (25, 27), (27, 29), (29, 31), (27, 31),  # Left leg
    (24, 26), (26, 28), (28, 30), (30, 32), (28, 32),  # Right leg
]

# Initialize pose landmarker
def init_pose_landmarker():
    global pose_landmarker
    try:
        BaseOptions = mp.tasks.BaseOptions
        PoseLandmarker = mp.tasks.vision.PoseLandmarker
        PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
        VisionRunningMode = mp.tasks.vision.RunningMode
        
        options = PoseLandmarkerOptions(
            base_options=BaseOptions(model_asset_path="pose_landmarker_full.task"),
            running_mode=VisionRunningMode.IMAGE,
        )
        pose_landmarker = PoseLandmarker.create_from_options(options)
        return True
    except Exception as e:
        print(f"Error initializing pose landmarker: {e}")
        return False

# Callback for pose results
def on_results(result: vision.PoseLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
    global latest_landmarks
    if result.pose_landmarks:
        latest_landmarks = result.pose_landmarks
    else:
        latest_landmarks = None

# Database grabber
def get_db():
    conn = sqlite3.connect("motion_tracking.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return send_from_directory('.', 'home.html')

@app.route('/api/start', methods=['POST'])
def start_recording():
    global camera, recording, frame_counter, frame_times
    try:
        camera = cv2.VideoCapture(0)
        if not camera.isOpened():
            return jsonify({'error': 'Cannot open webcam'}), 400
        
        frame_counter = 0
        frame_times = []  # Reset for accurate FPS measurement
        recording = True
        return jsonify({'status': 'Recording started'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stop', methods=['POST'])
def stop_recording():
    global camera, recording, out, frame_times
    try:
        recording = False
        if out is not None:
            out.release()
            out = None
        if camera:
            camera.release()
        frame_times = []  # Reset for next recording
        return jsonify({'status': 'Recording stopped'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/frame', methods=['GET'])
def get_frame():
    global camera, latest_frame, latest_landmarks, recording, out, video_writer_fps, video_writer_size, frame_counter, frame_times
    try:
        if not camera or not camera.isOpened():
            return jsonify({'error': 'Camera not initialized'}), 400
        
        ret, frame = camera.read()
        if not ret:
            return jsonify({'error': 'Cannot read frame'}), 400
        
        frame_counter += 1
        current_time = time.time()
        frame_times.append(current_time)
        
        # Keep only last 30 frames for FPS calculation
        if len(frame_times) > 30:
            frame_times.pop(0)
        
        # Optimize: Skip pose detection every other frame
        if frame_counter % 2 == 0:
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
            results = pose_landmarker.detect(mp_image)
            if results.pose_landmarks:
                latest_landmarks = results.pose_landmarks
        
        # Draw pose skeleton on frame
        h, w, c = frame.shape
        if latest_landmarks:
            # Draw connections first (so they appear behind the points)
            for pose in latest_landmarks:
                for connection in POSE_CONNECTIONS:
                    start_idx, end_idx = connection
                    # Skip connections that involve face landmarks
                    if start_idx <= 10 or end_idx <= 10:
                        continue
                    if start_idx < len(pose) and end_idx < len(pose):
                        start = pose[start_idx]
                        end = pose[end_idx]
                        x1, y1 = int(start.x * w), int(start.y * h)
                        x2, y2 = int(end.x * w), int(end.y * h)
                        cv2.line(frame, (x1, y1), (x2, y2), (255, 255, 255), 2)
            
            # Draw landmark points (skip face landmarks 0-10)
            for pose in latest_landmarks:
                for idx, landmark in enumerate(pose):
                    if idx <= 10:  # Skip face landmarks
                        continue
                    x = int(landmark.x * w)
                    y = int(landmark.y * h)
                    # White circle
                    cv2.circle(frame, (x, y), 5, (255, 255, 255), -1)
                    # Orange circle
                    cv2.circle(frame, (x, y), 4, (0, 165, 255), -1)
        
        # Draw recording indicator
        if recording:
            cv2.circle(frame, (20, 20), 8, (0, 0, 255), -1)
            cv2.putText(frame, "REC", (35, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        # Initialize video writer on first frame if recording
        if recording and out is None:
            # Calculate actual FPS from captured frames (after 10 frames)
            if len(frame_times) > 10:
                actual_fps = (len(frame_times) - 1) / (frame_times[-1] - frame_times[0])
                video_writer_fps = actual_fps
            else:
                video_writer_fps = 30.0
            
            video_writer_size = (w, h)
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            out = cv2.VideoWriter("motion_recording.mp4", fourcc, video_writer_fps, video_writer_size)
            print(f"Video recording started: {video_writer_fps:.2f} FPS, {video_writer_size} size")
        
        # Write frame directly to video file (no queuing)
        if recording and out is not None:
            out.write(frame)
        
        # Reduce JPEG quality to 70 for faster encoding
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
        frame_data = base64.b64encode(buffer).decode('utf-8')
        
        # Prepare landmarks data
        landmarks_data = []
        if latest_landmarks:
            for pose in latest_landmarks:
                for landmark in pose:
                    landmarks_data.append({
                        'x': float(landmark.x),
                        'y': float(landmark.y),
                        'z': float(landmark.z),
                        'visibility': float(landmark.visibility) if hasattr(landmark, 'visibility') else 1.0
                    })
        
        return jsonify({
            'frame': frame_data,
            'landmarks': landmarks_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    global camera, recording
    return jsonify({
        'camera_active': camera is not None and camera.isOpened(),
        'recording': recording
    })

# API endpoints for athletes and sessions
@app.route('/api/athletes')
def get_athletes():
    conn = get_db()
    rows = conn.execute("SELECT id, name FROM athletes ORDER BY name").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/sessions')
def get_sessions():
    conn = get_db()
    rows = conn.execute("""
        SELECT s.id, a.name AS athlete_name, s.started_at,
               r.metric_value
        FROM sessions s
        JOIN athletes a ON a.id = s.athlete_id
        LEFT JOIN results r ON r.session_id = s.id
                           AND r.metric_name = 'jump_height_in'
        WHERE s.session_type = 'jump'
        ORDER BY s.started_at DESC
        LIMIT 50
    """).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

if __name__ == '__main__':
    # Initialize pose landmarker on startup
    if init_pose_landmarker():
        print("Pose landmarker initialized successfully")
        app.run(debug=True, host='localhost', port=5000)
    else:
        print("Failed to initialize pose landmarker")
