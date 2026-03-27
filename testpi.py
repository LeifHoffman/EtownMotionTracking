import cv2
import mediapipe as mp
import time
import tkinter as tk

# ---- GUI Setup Using tkinter ----
def show_gui():
    global root
    root = tk.Tk()
    root.title("Save Recording?")
    root.geometry("300x200")

    def select_option(option):
        print(f'Selected Option: {option}')
        if option == "Option 1":
            print("Saving recording with name 'Leif Recording'")
        else:
            print("Deleting recording")
        root.destroy()

    # Create two buttons for options
    button1 = tk.Button(root, text="Save Recording", command=lambda: select_option("Option 1"))
    button1.pack(pady=20)

    button2 = tk.Button(root, text="Delete Recording", command=lambda: select_option("Option 2"))
    button2.pack(pady=20)

    root.mainloop()

# ---- Setup MediaPipe PoseLandmarker ----

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# Path to your downloaded model file (.task)
# Download the Pose Landmarker model as per the docs
model_path = "pose_landmarker_full.task"  # Update this path to your model file

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
leftFrame = False

# ---- OpenCV Webcam Loop ----

from picamera2 import Picamera2

picam2 = Picamera2()
preview_config = picam2.create_preview_configuration(main={"size": (640, 480)})
picam2.configure(preview_config)
picam2.start()

prev = 0
# Recording state
recording = False
out = None
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
writer_fps = None
writer_size = None

print("PiCamera2 started successfully. Starting pose tracking...")

try:
    while True:
        frame = picam2.capture_array()
        success = frame is not None
        if not success or frame is None:
            print(f"ERROR: frame capture failed - success={success}, frame_type={type(frame)}")
            break

        # Optional: flip frame if needed
        frame = cv2.flip(frame, 1)

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
                    

        # If recording, write the frame
        if recording and out is not None:
            out.write(frame)

        # Draw recording indicator
        if leftFrame or (recording and allcaptured == False):
            # If recording but not all points captured, show warning
            cv2.circle(frame, (20, 20), 8, (0, 255, 255), -1)
            cv2.putText(frame, "WARNING: LEFT FRAME", (35, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            leftFrame = True
        elif recording:
            cv2.circle(frame, (20, 20), 8, (0, 0, 255), -1)
            cv2.putText(frame, "REC", (35, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        elif recording == False and allcaptured == False:
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
                # Initialize writer on first record start to get actual frame size/fps
                if writer_fps is None:
                    writer_fps = 30.0  # Default for PiCamera2
                if writer_size is None:
                    h, w = frame.shape[:2]
                    writer_size = (w, h)
                # TODO Update 'name' variable to be dynamic based on user input
                name = "Leif Recording"
                filename = f"recording_{name}.mp4"
                out = cv2.VideoWriter(filename, fourcc, writer_fps, writer_size)
                print(f"Recording started -> {filename}")
            else:
                if out is not None:
                    out.release()
                    out = None
                print("Recording stopped")
                if leftFrame:
                    show_gui()
                leftFrame = False  # Reset left frame warning when recording stops

finally:
    landmarker.close()
    if out is not None:
        out.release()
    picam2.stop()
    cv2.destroyAllWindows()
