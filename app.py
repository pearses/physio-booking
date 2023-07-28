from flask import Flask, render_template, request, jsonify, session, redirect
from models import User, Appointment
from dto.appointment_dto import AppointmentDTO
from datetime import date, time


app = Flask(__name__)
app.secret_key = "P@ssword123"

users = [] # Swap with database integration

# --- User Login Service ---
def verify_user_credentials(email, password):
    user = next((user for user in users if user.email == email and user.password == password), None)
    return user


# --- Appointments ---

class AppointmentService:
    def __init__(self):
        self.appointments = []

    def time_slot_available(self, date, time):
        for appointment in self.appointments:
            if appointment.date == date and appointment.time == time:
                return False
        return True

    def create_appointment(self, date, time, logged_in_user):
        if not self.time_slot_available(date, time):
            return None, 'This time slot is no longer available'

        appointment_id = len(self.appointments) + 1
        appointment = Appointment(appointment_id, date, time, logged_in_user)
        self.appointments.append(appointment)
        return appointment, None

    def get_appointments(self):
        return self.appointments

    def cancel_appointment(self, appointment_id):
        for appointment in self.appointments:
            if appointment.appointment_id == appointment_id:
                self.appointments.remove(appointment)
                return True
        return False

appointment_service = AppointmentService()

# --- API Endpoints ---

@app.route('/')
def home_page():
    return render_template("index.html", title=home_page)

@app.route('/login_page')
def login_page():
    return render_template("login_page.html", title=login)

@app.route('/register_form')
def register_page():
    return render_template("register_form.html", title=register)

# User register
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data['email']
    password = data['password']
    patient_name = data['patient_name']

    # Basic validation: Check if email and password are not empty
    if not email or not password:
        return jsonify({'message': 'Email, password and patient_name are required.'}), 400

    # Validate email format (you can use a more robust email validation method)
    if '@' not in email:
        return jsonify({'message': 'Invalid email format.'}), 400

    # Validate password (you can implement a stronger password policy)
    if len(password) < 6:
        return jsonify({'message': 'Password must be at least 6 characters long.'}), 400

    # Check if the user with the provided email already exists
    if any(user.email == email for user in users):
        return jsonify({'message': 'Email already registered.'}), 400

    user_id = len(users) + 1
    new_user = User(user_id, email, password, patient_name)
    users.append(new_user)

    # Set up a session for the newly registered user
    session['user_id'] = new_user.user_id

    return jsonify({'message': 'Registration successful.'}), 201


# User login route
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Check if the provided credentials are valid
    user = verify_user_credentials(email, password)

    if user:
        # Set up a session for the authenticated user
        session['user_id'] = user.user_id
        session['user_email'] = user.email
        return jsonify({'message': 'Login successful.'}), 200
    else:
        return jsonify({'message': 'Invalid credentials.'}), 401
    

# User Logout route
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user.id', None)
    return jsonify({'message': 'Logged out successfully.'}), 200


# Fetch List of Users
@app.route('/users', methods=['GET'])
def view_users():
    user_data = [{'user_id': user.user_id, 'email': user.email} for user in users]
    return jsonify(user_data), 200


# Delete Users
@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = next((user for user in users if user.user_id == user_id), None)
    if user:
        user_email = user.email  # Fetch the user's email
        users.remove(user)
        return jsonify({'message': f"User {user_email} has been deleted."}), 200
    else:
        return jsonify({'message': 'User not found.'}), 404
    



@app.route('/appointments', methods=['POST'])
def create_appointment():
    logged_in_user = session.get('user_email', None)

    if not logged_in_user:
        return jsonify({'message': 'User not logged in.'}), 401

    data = request.get_json()
    appointment_dto = AppointmentDTO(**data) 

    # Create the appointment with the patient_name from the logged-in user
    appointment, error_message = appointment_service.create_appointment(
        appointment_dto.date,
        appointment_dto.time,
        logged_in_user  # Use the patient_name fetched from the logged-in user
    )

    if appointment:
        return jsonify(appointment.__dict__)
    else:
        return jsonify({'message': error_message}), 400
    

@app.route('/appointments', methods=['GET'])
def view_appointments():
    appointments = appointment_service.get_appointments()
    appointment_data = [appointment.__dict__ for appointment in appointments]
    return jsonify(appointment_data)

@app.route('/appointments/<int:appointment_id>', methods=['DELETE'])
def cancel_appointment(appointment_id):
    canceled = appointment_service.cancel_appointment(appointment_id)
    if canceled:
        return jsonify({'message': 'Appointment canceled successfully.'}), 200
    return jsonify({'message': 'Appointment not found.'}), 404

#USE FOR FUTURE IMPLEMENTATION
#
#if __name__ == '__main__':
#    app.run()
