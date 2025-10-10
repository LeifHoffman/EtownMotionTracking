# import libraries for video capture and pose estimation
import cv2
import mediapipe as mp
# import libraries for console clearing
import os
import subprocess


mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

# counter variables for delay
delay_counter = 0
print_delay = 10

# Track velocity of given point
prev_point = None

# set cmd to clear console later
cmd = "cls" if os.name == "nt" else "clear"


cap = cv2.VideoCapture(0)  # change to video file path if you prefer

with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image)

        # draw landmarks
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        if results.pose_landmarks:
            mp_drawing.draw_landmarks(
                image,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS)

            # Example: access landmark coordinates (normalized x,y,z)
            # Nose = index 0 (see MediaPipe docs)
            lm = results.pose_landmarks.landmark
            #increment delay counter until delay reached
            if delay_counter < print_delay:
                delay_counter += 1
            else:
                nose = [lm[0].x, lm[0].y]
                if prev_point != None:
                    subprocess.call(cmd, shell=True)
                    print("Velocity X:", nose[0]-prev_point[0], "\nVelocity Y:", -(nose[1]-prev_point[1]))
                # Set to prev_point
                prev_point = nose
                # reset delay counter
                delay_counter = 0

        cv2.imshow('Pose', image)
        if cv2.waitKey(1) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()
