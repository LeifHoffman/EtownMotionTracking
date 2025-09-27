import cv2
import mediapipe as mp
import keyboard as kb

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

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
            # Nose = index 0, LEFT_ELBOW = 13, LEFT_KNEE = 25 (see MediaPipe docs)
            lm = results.pose_landmarks.landmark
            nose = (lm[0].x, lm[0].y, lm[0].z)
            left_elbow = (lm[13].x, lm[13].y, lm[13].z)
            left_knee = (lm[25].x, lm[25].y, lm[25].z)
            print("nose:", nose, "L_elbow:", left_elbow, "L_knee:", left_knee)

        cv2.imshow('Pose', image)
        if cv2.waitKey(1) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()
