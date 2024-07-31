import cv2
import numpy as np
import os
from mtcnn import MTCNN
import face_recognition

# Load the MTCNN model
detector = MTCNN()
print('Training started...')
# Function to extract face encodings using face_recognition
def extract_face_encodings(image):
    # Find all face locations in the image
    face_locations = face_recognition.face_locations(image)

    # If no face is found, return an empty list
    if not face_locations:
        return []

    # Encode faces found in the image
    face_encodings = face_recognition.face_encodings(image, known_face_locations=face_locations)

    return face_encodings

# Function to save face encodings to a file
def save_face_encodings(dataset_path, output_file):
    face_encodings_dict = {}
    for person_name in os.listdir(dataset_path):
        person_dir = os.path.join(dataset_path, person_name)
        if os.path.isdir(person_dir):
            face_encodings = []
            for filename in os.listdir(person_dir):
                image_path = os.path.join(person_dir, filename)
                image = cv2.imread(image_path)
                if image is not None:
                    # Convert image from BGR to RGB (required by face_recognition)
                    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    face_encodings += extract_face_encodings(image_rgb)
            if face_encodings:
                face_encodings_dict[person_name] = face_encodings
    np.savez(output_file, **face_encodings_dict)

if __name__ == "__main__":
    # Path to the dataset containing images of each person
    dataset_path = "static/images"
    # Output file to save face encodings
    output_file = "face_encodings.npz"
    # Save face encodings to the output file
    save_face_encodings(dataset_path, output_file)
