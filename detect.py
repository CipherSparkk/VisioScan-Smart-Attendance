import cv2
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import face_recognition
import csv
from datetime import datetime
import os

# Load the stored face encodings
face_encodings = np.load("face_encodings.npz", allow_pickle=True)

# Generate filename with current date
current_date = datetime.now().strftime("%Y-%m-%d")
folder_name = "attendance"
csv_filename = os.path.join(folder_name, f"attendance_{current_date}.csv")

# Initialize a dictionary to store recognized faces and their in-times
recognized_faces = {}

# Open CSV file in append mode
with open(csv_filename, mode='a', newline='') as csv_file:
    fieldnames = ['person', 'in_time']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    # Write header if the file is empty
    if csv_file.tell() == 0:
        writer.writeheader()

    # Function to recognize the face and update attendance
    def recognize_face(frame):
        # Convert the frame to RGB (as required by face_recognition library)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Detect faces using the HOG method (more accurate than Haar cascade for small faces)
        face_locations = face_recognition.face_locations(rgb_frame)

        # Encode the detected faces
        detected_face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        # Get current date and time
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Loop through each detected face
        for detected_face_encoding, (top, right, bottom, left) in zip(detected_face_encodings, face_locations):
            # Perform face recognition using loaded encodings
            best_match = ("Unknown", 0)
            for person_name, encodings in face_encodings.items():
                for encoding in encodings:
                    similarity_score = cosine_similarity([detected_face_encoding], [encoding])[0][0]
                    if similarity_score > best_match[1]:
                        best_match = (person_name, similarity_score)

            # If the similarity score is less than 95%, consider it as "Unknown"
            if best_match[1] < 0.95:
                best_match = ("Unknown", best_match[1])

            # Draw rectangle around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            
            # Add text with class name and probability
            cv2.putText(frame, f"{best_match[0]} - {best_match[1]:.2%}", (left, top-10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 1, cv2.LINE_AA)
            
            # Write to CSV if the person is recognized and it's the first detection in this frame
            if best_match[0] != "Unknown" and best_match[0] not in recognized_faces:
                recognized_faces[best_match[0]] = current_time
                writer.writerow({'person': best_match[0], 'in_time': current_time})
        
        return frame

    # Open the webcam
    cap = cv2.VideoCapture(0)
    # Set the desired width and height for resizing
    desired_width = 1200
    desired_height = 750

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Resize the frame
        frame = cv2.resize(frame, (desired_width, desired_height))

        # Recognize faces in the frame and update attendance
        frame = recognize_face(frame)

        # Display the frame
        cv2.imshow('Face Recognition', frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the video capture object and close all windows
    cap.release()
    cv2.destroyAllWindows()
