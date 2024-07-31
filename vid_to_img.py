import cv2
import numpy as np
import os

# Function to create a folder if it doesn't exist
def create_folder(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

# Function to extract frames from video at a given interval
def extract_frames(video_path, output_folder, interval=0.05):
    # Open the video file
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Unable to open video file '{video_path}'")
        return

    # Create the output folder if it doesn't exist
    create_folder(output_folder)

    # Set the frame rate
    fps = cap.get(cv2.CAP_PROP_FPS)
    interval_frames = int(fps * interval)

    # Read and save frames at regular intervals
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Save the frame
        if frame_count % interval_frames == 0:
            image_name = os.path.join(output_folder, f"snapshot_{frame_count // interval_frames}.jpg")
            cv2.imwrite(image_name, frame)
            print(f"Saved snapshot: {image_name}")

        frame_count += 1

    # Release the video capture object
    cap.release()

# Folder containing video files
videos_folder = "static/videos"

# Output folder for snapshots
output_root_folder = "static/images"

# Process each video file in the videos folder
for video_file in os.listdir(videos_folder):
    if video_file.endswith(".mov") or video_file.endswith(".mp4"):
        video_name = os.path.splitext(video_file)[0]
        video_path = os.path.join(videos_folder, video_file)
        output_folder = os.path.join(output_root_folder, video_name)
        extract_frames(video_path, output_folder)
