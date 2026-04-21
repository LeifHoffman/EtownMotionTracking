import cv2
import mediapipe as mp
import time
import tkinter as tk
from tkinter import ttk
import os
import sys

# ---- GUI Setup Using tkinter ----
def show_gui(filename=None):
    global root
    root = tk.Tk()
    root.title("Save Recording?")
    root.geometry("300x200")

    def select_option(option):
        print(f'Selected Option: {option}')
        if option == "Option 1":
            print("Saving recording")
        else:
            print("Deleting recording")
            # Delete the recording file if it exists and filename is provided
            if filename and os.path.exists(filename):
                os.remove(filename)
                print(f"Deleted file: {filename}")
            # Also delete the temp .avi if it exists
            if filename:
                avi_file = filename.replace(".mp4", "_tmp.avi")
                if os.path.exists(avi_file):
                    os.remove(avi_file)
        root.destroy()

    # Create two buttons for options
    button1 = tk.Button(root, text="Save Recording", command=lambda: select_option("Option 1"))
    button1.pack(pady=20)

    button2 = tk.Button(root, text="Delete Recording", command=lambda: select_option("Option 2"))
    button2.pack(pady=20)

    root.mainloop()

# ---- Name Selection using tkinter ----
def get_user_name():
    global root, selected_user
    root = tk.Tk()
    root.title("Select a user")
    root.geometry("300x200")

    selected_user = None

    # List of athletes
    athletes = ["Vincent", "Evan", "James", "Leif", "Sarah", "Emma", "Michael", "Jessica"]

    # Create label
    label = tk.Label(root, text="Select an athlete:", font=("Arial", 12))
    label.pack(pady=10)

    # Create combobox
    combobox = ttk.Combobox(root, values=athletes, state="readonly", width=25)
    combobox.pack(pady=10)
    combobox.current(0)  # Set default selection to first item

    def confirm_selection():
        global selected_user
        selected_user = combobox.get()
        print(f'Selected Athlete: {selected_user}')
        root.destroy()

    # Create confirm button
    button = tk.Button(root, text="Confirm", command=confirm_selection)
    button.pack(pady=20)

    root.mainloop()

    return selected_user

# ---- Helper: convert .avi to .mp4 using ffmpeg ----
def convert_to_mp4(avi_path, mp4_path):
    """Convert a raw XVID .avi file to H.264 .mp4 using ffmpeg."""
    print(f"Converting {avi_path} -> {mp4_path} ...")
    ret = os.system(f'ffmpeg -y -i "{avi_path}" -vcodec libx264 -preset fast -crf 23 "{mp4_path}"')
    if ret == 0 and os.path.exists(mp4_path) and os.path.getsize(mp4_path) > 1024:
        os.remove(avi_path)
        print(f"Conversion successful: {mp4_path}")
    else:
        print(f"WARNING: ffmpeg conversion failed (exit code {ret}). Keeping raw .avi: {avi_path}")

# ---- Setup MediaPipe PoseLandmarker ----

# Use command-line argument for selected athlete name when provided
if len(sys.argv) > 1:
    name = sys.argv[1]
    print(f"Selected athlete from CLI arg: {name}")
else:
    name = None

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# Path to your downloaded model file (.task)
# Download the Pose Landmarker model as per the docs
model_path = os.path.join(os.path.dirname(__file__), "pose_landmarker_full.task")

# Store latest landmarks
latest_landmarks = None

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

# Callback to receive landmarks results
def on_results(result: vision.PoseLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
    global latest_landmarks
    # result.landmarks is a list of POSE landmarks per detected person
    if result.pose_landmarks:
        latest_landmarks = result.pose_landmarks
    else:
        latest_landmarks = None

# Helper to extract body landmark positions for motion measurement
def get_body_landmark_positions(pose, indices):
    positions = []
    for idx in indices:
        if idx < len(pose) and getattr(pose[idx], 'visibility', 1.0) > 0.5:
            positions.append((pose[idx].x, pose[idx].y))
    return positions

# Compute average normalized movement between two poses
def compute_pose_motion(prev_pose, current_pose, indices):
    prev_positions = get_body_landmark_positions(prev_pose, indices)
    curr_positions = get_body_landmark_positions(current_pose, indices)
    if not prev_positions or not curr_positions or len(prev_positions) != len(curr_positions):
        return 0.0
    distances = [((px - cx) ** 2 + (py - cy) ** 2) ** 0.5
                 for (px, py), (cx, cy) in zip(prev_positions, curr_positions)]
    return sum(distances) / len(distances)

BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

options = PoseLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.LIVE_STREAM,
    result_callback=on_results,
)

landmarker = PoseLandmarker.create_from_options(options)

# Variables for tracking if user is in frame or left frame
allcaptured = False
enable_warning = False
leftFrame = False

# ---- PiCamera2 Setup ----
from picamera2 import Picamera2

picam2 = Picamera2()
preview_config = picam2.create_preview_configuration(main={"size": (640, 480)})
picam2.configure(preview_config)
picam2.start()

prev = 0
# Recording state, automatically start recording if name provided via CLI arg, otherwise wait for 'r' key
if len(sys.argv) > 1:
    recording = True
else:
    recording = False

out = None
# FIX: Use XVID codec writing to a temp .avi file, then convert to .mp4 with ffmpeg.
# mp4v is broken on Raspberry Pi / Linux OpenCV builds and produces empty ~258 byte files.
fourcc = cv2.VideoWriter_fourcc(*"XVID")
writer_fps = None
writer_size = None
filename = None      # final .mp4 path
avi_filename = None  # temp .avi path

# Movement detection state for automatic stop
prev_pose = None
is_moving = False
movement_still_start = None
movement_still_duration_threshold = 2.0  # seconds
movement_motion_threshold = 0.015
movement_still_threshold = 0.008

print("PiCamera2 started successfully. Starting pose tracking...")

def start_writer(frame, athlete_name):
    """Initialise the VideoWriter and return (out, avi_filename, mp4_filename)."""
    fps = 30.0
    h, w = frame.shape[:2]
    size = (w, h)
    os.makedirs("recordings", exist_ok=True)
    mp4_path = f"recordings/recording_{athlete_name}.mp4"
    avi_path = f"recordings/recording_{athlete_name}_tmp.avi"
    writer = cv2.VideoWriter(avi_path, fourcc, fps, size)
    if not writer.isOpened():
        print("ERROR: VideoWriter failed to open — check that XVID codec is available")
    else:
        print(f"Recording started -> {avi_path} (will convert to {mp4_path} on stop)")
    return writer, fps, size, avi_path, mp4_path

def stop_writer(writer, avi_path, mp4_path):
    """Release the writer and convert the .avi to .mp4."""
    writer.release()
    convert_to_mp4(avi_path, mp4_path)
    return mp4_path

try:
    while True:
        # Capture frame from PiCamera2
        frame = picam2.capture_array()
        success = frame is not None
        if not success or frame is None:
            print(f"ERROR: frame capture failed - success={success}, frame_type={type(frame)}")
            break

        # Optional: flip frame if needed
        frame = cv2.flip(frame, 1)

        # PiCamera2 outputs RGB (or RGBA); convert to BGR for correct OpenCV display and writing
        if frame.ndim == 3 and frame.shape[2] == 4:
            frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)
        else:
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # Initialize video writer if recording started and not yet initialized
        if recording and out is None:
            if name is None:
                if len(sys.argv) > 1:
                    name = sys.argv[1]
                else:
                    name = get_user_name()
            out, writer_fps, writer_size, avi_filename, filename = start_writer(frame, name)

        # MediaPipe wants RGB images, OpenCV gives BGR
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Convert to mediapipe.Image
        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB, data=rgb_frame
        )

        # Send the frame to the landmarker async
        timestamp_ms = int(time.time() * 1000)
        landmarker.detect_async(mp_image, timestamp_ms)

        # Check if all wanted points (11-32) are captured
        if latest_landmarks and len(latest_landmarks) > 0:
            pose = latest_landmarks[0]  # Assume single person
            wanted_indices = range(11, 33)  # Body pose points (skip face 0-10)
            visibility_threshold = 0.5  # Adjust as needed for stricter/looser detection
            allcaptured = all(
                idx < len(pose) and pose[idx].visibility > visibility_threshold
                for idx in wanted_indices
            )
        else:
            allcaptured = False

        # Draw landmarks on frame
        if latest_landmarks:
            h, w = frame.shape[:2]

            # Draw connections first (so they appear behind the points)
            # Skip face landmarks (indices 0-10)
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

        # Movement detection for automatic stop when user stops moving
        if latest_landmarks and len(latest_landmarks) > 0 and recording and allcaptured:
            current_pose = latest_landmarks[0]
            motion = 0.0
            if prev_pose is not None:
                motion = compute_pose_motion(prev_pose, current_pose, range(11, 33))
            if motion > movement_motion_threshold:
                is_moving = True
                movement_still_start = None
            elif is_moving and motion < movement_still_threshold:
                if movement_still_start is None:
                    movement_still_start = time.time()
                elif time.time() - movement_still_start >= movement_still_duration_threshold:
                    recording = False
                    if out is not None:
                        filename = stop_writer(out, avi_filename, filename)
                        out = None
                    print("Recording auto-stopped because user stopped moving")
                    leftFrame = False
                    enable_warning = False
                    is_moving = False
                    movement_still_start = None
            else:
                movement_still_start = None
            prev_pose = current_pose
        elif not allcaptured:
            # Reset motion tracking until all points are captured again
            prev_pose = None
            is_moving = False
            movement_still_start = None

        # If recording, write the frame.
        # PiCamera2 may return XRGB8888 (4-channel); VideoWriter requires BGR (3-channel).
        # Converting here ensures frames are always written correctly.
        if recording and out is not None:
            out.write(frame)

        # Enable warning once user is in full frame
        if recording and allcaptured:
            enable_warning = True

        # Draw recording indicator
        if leftFrame or (recording and allcaptured is False and enable_warning):
            # If recording but not all points captured, show warning
            cv2.circle(frame, (20, 20), 8, (0, 255, 255), -1)
            cv2.putText(frame, "WARNING: LEFT FRAME", (35, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            leftFrame = True
        elif recording and allcaptured is False:
            cv2.circle(frame, (20, 20), 8, (0, 255, 255), -1)
            cv2.putText(frame, "MOVE INTO POSITION", (35, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        elif recording:
            cv2.circle(frame, (20, 20), 8, (0, 0, 255), -1)
            cv2.putText(frame, "REC", (35, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        elif not recording and not allcaptured:
            cv2.putText(frame, "OUT OF FRAME", (35, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (169, 169, 169), 2)
        else:
            cv2.putText(frame, "READY", (35, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 150, 0), 2)

        # Draw frame so you see video
        cv2.imshow("Webcam Pose Tracking", frame)
        if cv2.getWindowProperty("Webcam Pose Tracking", cv2.WND_PROP_VISIBLE) < 1:
            print("INFO: window closed or not visible - exiting loop")
            break

        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC to quit
            break
        # Toggle recording with 'r'
        if key == ord('r'):
            recording = not recording
            if recording:
                # Initialize writer if not already initialized
                if out is None:
                    if name is None:
                        name = get_user_name()
                    out, writer_fps, writer_size, avi_filename, filename = start_writer(frame, name)
            else:
                if out is not None:
                    filename = stop_writer(out, avi_filename, filename)
                    out = None
                print("Recording stopped")
                if leftFrame:
                    show_gui(filename)
                leftFrame = False  # Reset left frame warning when recording stops
                enable_warning = False  # Reset warning state when recording stops
                name = None  # Reset name for next recording

        # Exit if recording stopped and name was provided via CLI
        if not recording and len(sys.argv) > 1:
            print("Exiting after recording stop with CLI arg")
            break

finally:
    landmarker.close()
    if out is not None:
        # Ensure we convert any in-progress recording on unexpected exit
        if avi_filename and filename:
            stop_writer(out, avi_filename, filename)
        else:
            out.release()
    picam2.stop()
    cv2.destroyAllWindows()