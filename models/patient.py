class Patient:
    def __init__(self, patient_id, name, contact_details, medical_history):
        self.patient_id = patient_id
        self.name = name
        self.contact_details = contact_details
        self.medical_history = medical_history

    def update_contact_details(self, new_contact_details):
        self.contact_details = new_contact_details

    def update_medical_history(self, new_medical_history):
        self.medical_history = new_medical_history
