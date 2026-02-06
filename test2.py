import cv2
import mediapipe as mp
import time

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
        for i, single_pose in enumerate(result.pose_landmarks):
            print(f"Pose {i} landmarks count:", len(single_pose))
            # single_pose contains x/y/z coords for each body landmark
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

# ---- OpenCV Webcam Loop ----

cap = cv2.VideoCapture(0)
prev = 0

try:
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
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

        # Draw landmarks on frame
        if latest_landmarks:
            h, w = frame.shape[:2]
            
            # Draw connections first (so they appear behind the points)
            for pose in latest_landmarks:
                for connection in POSE_CONNECTIONS:
                    start_idx, end_idx = connection
                    if start_idx < len(pose) and end_idx < len(pose):
                        start = pose[start_idx]
                        end = pose[end_idx]
                        x1, y1 = int(start.x * w), int(start.y * h)
                        x2, y2 = int(end.x * w), int(end.y * h)
                        cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Draw landmark points
            for pose in latest_landmarks:
                for landmark in pose:
                    x = int(landmark.x * w)
                    y = int(landmark.y * h)
                    cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)

        # Draw frame so you see video
        cv2.imshow("Webcam Pose Tracking", frame)
        if cv2.waitKey(5) & 0xFF == ord("q"):
            break

finally:
    landmarker.close()
    cap.release()
    cv2.destroyAllWindows()
