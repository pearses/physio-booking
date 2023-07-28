from models.appointment import Appointment

class AppointmentService:
    def __init__(self):
        self.appointments = []

    def create_appointment(self, date, time, patient_name):
        appointment_id = len(self.appointments) + 1
        appointment = Appointment(appointment_id, date, time, patient_name)
        self.appointments.append(appointment)
        return appointment

    def view_appointments(self):
        return self.appointments
    
    def cancel_appointment(self, appointment_id):
        for appointment in self.appointments:
            if appointment.appointment_id == appointment_id:
                self.appointments.remove(appointment)
                return True
        return False