# import libraries for video capture and pose estimation
import cv2
import mediapipe as mp
# import libraries for console clearing
import os
import subprocess
# import library for math calculation
import math

# PLEASE REMOVE THIS IS A JOKE
import random

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

# counter variables for delay
delay_counter = 0
print_delay = 10

# Track velocity of given point
prev_point = None

# set cmd to clear console later
cmd = "cls" if os.name == "nt" else "clear"

# change to video file path if you prefer
cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)  
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# video writer to save output video
fourcc = cv2.VideoWriter_fourcc(*"XVID")
out = cv2.VideoWriter("camera_recording.avi", fourcc, 20.0, (1280, 720))

with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image)

        # draw landmarks
        # draw landmarks
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        if results.pose_landmarks:
            # Filter out landmarks 0-10 (upper body/head)
            filtered_landmarks = mp.solutions.pose.PoseLandmark
            landmarks_to_draw = []
            for idx, landmark in enumerate(results.pose_landmarks.landmark):
                if idx > 10:  # Only include landmarks after index 10
                    landmarks_to_draw.append(landmark)
            
            # Manually draw circles for filtered landmarks
            h, w, c = image.shape
            for landmark in landmarks_to_draw:
                x = int(landmark.x * w)
                y = int(landmark.y * h)
                # Change the color of the below circle to something consistent
                cv2.circle(image, (x, y), 2, (255, 255, 225), 5)
                cv2.circle(image, (x, y), 1, (0, 165, 225), 5)

            # Draw connections between filtered landmarks
            lm = results.pose_landmarks.landmark
            connections = [
                (11, 12), (12, 14), (14, 16), (11, 13), (13, 15),  # Arms (indices > 10)
                (23, 24), (24, 26), (26, 28), (23, 25), (25, 27),  # Legs
                (11, 23), (12, 24),  # Torso to legs
                (16, 18), (16, 20), (18, 20),  # Right hand
                (15, 17), (15, 19), (17, 19)   # Left hand
            
            ]
            
            for start, end in connections:
                if start > 10 and end > 10:  # Only draw if both points are after index 10
                    x1 = int(lm[start].x * w)
                    y1 = int(lm[start].y * h)
                    x2 = int(lm[end].x * w)
                    y2 = int(lm[end].y * h)
                    # TODO: Please change the color of the below line to something consistent
                    cv2.line(image, (x1, y1), (x2, y2), (255,255,255), 2)

            #increment delay counter until delay reached
            if delay_counter < print_delay:
                delay_counter += 1
            else:
                # Get nose coords (please change later)
                nose = [lm[0].x, lm[0].y]
                # Get right leg coords
                right_leg_upper = [lm[24].x, lm[24].y]
                right_leg_mid = [lm[26].x, lm[26].y]
                right_leg_lower = [lm[28].x, lm[28].y]
                # Get left leg coords
                left_leg_upper = [lm[23].x, lm[23].y]
                left_leg_mid = [lm[25].x, lm[25].y]
                left_leg_lower = [lm[27].x, lm[27].y]
                # Check visibility score
                visibility_score = round(lm[0].visibility, 3)
                if visibility_score >= 0.95:
                    if prev_point != None:
                        # clear console
                        subprocess.call(cmd, shell=True)
                        print("Velocity X:", round(nose[0]-prev_point[0], 3), "\nVelocity Y:", round(-(nose[1]-prev_point[1]), 3))
                        print("Right Leg Angle:", round((math.degrees(math.atan2(right_leg_lower[1]-right_leg_mid[1], right_leg_lower[0]-right_leg_mid[0]) - math.atan2(right_leg_upper[1]-right_leg_mid[1], right_leg_upper[0]-right_leg_mid[0])))%180, 2))
                        print("Left Leg Angle:", round((math.degrees(math.atan2(left_leg_lower[1]-left_leg_mid[1], left_leg_lower[0]-left_leg_mid[0]) - math.atan2(left_leg_upper[1]-left_leg_mid[1], left_leg_upper[0]-left_leg_mid[0])))%180, 2))
                        print("Confidence Score:", visibility_score)
                else:
                    subprocess.call(cmd, shell=True)
                    print("Low Confidence Score:", visibility_score)
                # Set to prev_point
                prev_point = nose
                # reset delay counter
                delay_counter = 0

        cv2.imshow('Pose', image)
        out.write(image)

        # ESC key stops recording
        if cv2.waitKey(1) == 27:
            break

cap.release()
out.release()
cv2.destroyAllWindows()
