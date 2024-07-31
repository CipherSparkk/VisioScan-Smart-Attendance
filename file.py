from flask import Flask, render_template, request, redirect, url_for
import subprocess
from flask_sqlalchemy import SQLAlchemy
from flask import jsonify 
from flask import render_template
import os
import csv

app = Flask(__name__, static_url_path='/static')
app.secret_key = 'mySecretKey'

app.config['STATIC_FOLDER'] = 'static'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:root@127.0.0.1:3306/university'  # Replace with your MySQL URI
db = SQLAlchemy(app)

class Students(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    current_year = db.Column(db.String(50))
    department = db.Column(db.String(100))
    reg_no = db.Column(db.String(20))
    roll_no = db.Column(db.String(20))
    student_name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/student_detail')
def student_detail():
    return render_template('student_detail.html')

# New route for executing detect.py
@app.route('/run_face_detector')
def run_face_detector():
    # Execute detect.py using subprocess
    subprocess.Popen(['python', 'detect.py'])
    return redirect(url_for('home'))  # Redirect to home page after execution

@app.route('/save_student', methods=['POST'])
def save_student():
    current_year = request.form['current-year']
    department = request.form['department']
    reg_no = request.form['reg-no']
    roll_no = request.form['roll-no']
    student_name = request.form['student-name']
    email = request.form['email']
    phone = request.form['phone']
    address = request.form['address']

    existing_student = Students.query.filter((Students.reg_no == reg_no) | (Students.roll_no == roll_no)).first()
    if existing_student:
        # Student with the same registration number or roll number already exists
        return render_template('student_existed.html')
    else:
        new_student = Students(
            current_year=current_year,
            department=department,
            reg_no=reg_no,
            roll_no=roll_no,
            student_name=student_name,
            email=email,
            phone=phone,
            address=address
        )
        db.session.add(new_student)
        db.session.commit()

    return render_template('student_data_saved.html')

@app.route('/student_database')
def student_database():
    # Retrieve all students from the database
    students = Students.query.all()
    # Render the template and pass the student data to it
    return render_template('student_database.html', students=students)

@app.route('/student/<int:student_id>')
def student(student_id):
    # Fetch student information from the database based on student_id
    data = Students.query.get(student_id)
    if student:
       return render_template('student.html', student=data)
    else:
        # Handle case where student with given ID is not found
        return render_template('error.html', message='Student not found')  # You can customize the error message and status code as needed
    
    
@app.route('/update_student/<int:student_id>', methods=['POST'])
def update_student(student_id):
    current_year = request.form['current-year']
    department = request.form['department']
    reg_no = request.form['reg-no']
    roll_no = request.form['roll-no']
    student_name = request.form['student-name']
    email = request.form['email']
    phone = request.form['phone']
    address = request.form['address']

    student = Students.query.get(student_id)
    if student:
        student.current_year = current_year
        student.department = department
        student.reg_no = reg_no
        student.roll_no = roll_no
        student.student_name = student_name
        student.email = email
        student.phone = phone
        student.address = address
        db.session.commit()
        return redirect(url_for('home'))
    else:
        return render_template('error.html', message='Student not found')



    
@app.route('/delete_student/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    student = Students.query.get(student_id)
    if student:
        db.session.delete(student)
        db.session.commit()
        return jsonify({'message': 'Student deleted successfully'}), 200
    else:
        return jsonify({'error': 'Student not found'}), 404


@app.route('/attendance_records')
def attendance_records():
    # Get list of CSV files in the "attendance" folder
    attendance_folder = "attendance"
    csv_files = [f for f in os.listdir(attendance_folder) if f.endswith('.csv')]
    # Extract file names without extensions
    file_names = [os.path.splitext(f)[0] for f in csv_files]
    # Render attendance_records.html and pass the file names to it
    return render_template('attendance_records.html', file_names=file_names)

@app.route('/attendance_records/<file_name>')
def display_attendance(file_name):
    # Construct the path to the CSV file
    file_path = os.path.join("attendance", f"{file_name}.csv")
    # Check if the file exists
    if os.path.exists(file_path):
    # Read the contents of the CSV file
        with open(file_path, 'r') as file:
            # Parse the CSV data
            csv_reader = csv.reader(file)
        
            # Get the header row
            header_row = next(csv_reader)
            
            # Convert CSV data to HTML table format
            table_html = '<table border="1">'
            
            # Add table header
            table_html += '<tr>'
            for column in header_row:
                table_html += f'<th>{column.capitalize()}</th>'
            table_html += '</tr>'
            
            # Add table rows
            for row in csv_reader:
                table_html += '<tr>'
                for column in row:
                    table_html += f'<td>{column.capitalize()}</td>'
                table_html += '</tr>'
            
            table_html += '</table>'
            
        # Return the HTML table in the response
        return table_html
    else:
        # Handle case where file does not exist
        return render_template('error.html', message='Attendance record not found')
    
@app.route('/delete_attendance/<file_name>', methods=['DELETE'])
def delete_attendance(file_name):
    file_path = os.path.join("attendance", f"{file_name}.csv")
    if os.path.exists(file_path):
        os.remove(file_path)
        return jsonify({'message': 'Attendance record deleted successfully'}), 200
    else:
        return jsonify({'error': 'Attendance record not found'}), 404


@app.route('/data')
def data():
    return render_template('data.html')

@app.route('/add_data')
def add_data():
    return render_template('add_data.html')

@app.route('/video_data')
def video_data():
    # Define the path to the videos folder
    videos_folder = './static/videos'

    # Get the list of video names within the videos folder
    video_names = [name for name in os.listdir(videos_folder) if os.path.isfile(os.path.join(videos_folder, name)) and (name.endswith('.mp4') or name.endswith('.mov'))]

    # Render the video_data.html template and pass the video names to it
    return render_template('video_data.html', video_names=video_names)

@app.route('/image_data')
def image_data():
    # Define the path to the images folder
    images_folder = './static/images'

    # Get the list of folder names within the images folder
    folder_names = [name for name in os.listdir(images_folder) if os.path.isdir(os.path.join(images_folder, name))]

    # Render the image_data.html template and pass the folder names to it
    return render_template('image_data.html', folder_names=folder_names)

@app.route('/student_images/<folder_name>')
def student_images(folder_name):
    # Define the path to the folder containing the images
    images_folder = f'./static/images/{folder_name}'

    # Get the list of image names within the folder
    image_names = [name for name in os.listdir(images_folder) if os.path.isfile(os.path.join(images_folder, name))]

    # Render the student_images.html template and pass the image names and folder name to it
    return render_template('student_images.html', folder_name=folder_name, image_names=image_names)



@app.route('/validate_student', methods=['POST'])
def validate_student():
    data = request.get_json()
    student_name = data.get('studentName')
    reg_no = data.get('regNo')
    roll_no = data.get('rollNo')

    # Check if a student with the provided registration number or roll number exists
    existing_student = Students.query.filter((Students.reg_no == reg_no) | (Students.roll_no == roll_no) | (Students.student_name == student_name)).first()

    if existing_student:
        # Student already exists, validation failed
        valid = True
    else:
        # Student does not exist, validation successful
        valid = False

    return jsonify({'valid': valid})

@app.route('/save_video', methods=['POST'])
def save_video():
    # Check if the request contains a file
    if 'video' not in request.files:
        return 'No file part'
    
    file = request.files['video']
    
    # If the user does not select a file, the browser submits an empty file without a filename
    if file.filename == '':
        return 'No selected file'
    
    # Define the folder where you want to save the video
    upload_folder = './static/videos'
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    
    # Save the uploaded file to the specified folder
    file.save(os.path.join(upload_folder, file.filename))
    
    # Perform any additional actions, such as saving other form data to the database
    
    # Display an alert message upon successful upload
    message = 'Video Uploaded Successfully'
    
    # Redirect to the home page
    return redirect('/')

@app.route('/train_data')
def train_data():
    return render_template('train_data.html')

@app.route('/run_vid_to_img')
def run_vid_to_img():
    # Execute vid_to_img.py using subprocess
    process = subprocess.Popen(['python', 'vid_to_img.py'])
    # Wait for the process to complete
    process.wait()
    # Return a JSON response after completion
    return jsonify({'message': 'Data gathered'})

@app.route('/run_train')
def run_train():
    # Execute train.py using subprocess
    process = subprocess.Popen(['python', 'train.py'])
    # Wait for the process to complete
    process.wait()
    # Return a JSON response after completion
    return jsonify({'message': 'Model trained successfully'})

if __name__ == '__main__':
    app.run(debug=True)
