# UMCEMR - Patient Portal

**UMCEMR (Unilag Medical Center Electronic Medical Record System)** is a modern web application designed to improve healthcare delivery at the University of Lagos Medical Center.  
This patient-facing portal enables students, staff, and patients to **book doctor appointments, access medical records, and manage their healthcare journey** seamlessly.  

The system integrates a **React frontend**, **FastAPI backend**, and **Odoo EMR** for robust record management, ensuring a smooth and secure healthcare experience.  

---

## Features

### For Patients
1. **Doctor & Clinic Discovery**
   - Browse doctors by clinic type or specialization  
   - View detailed profiles including qualifications and consultation schedules  
   - Filter doctors based on availability  

2. **Appointment Management**
   - Book appointments with available doctors  
   - View real-time time slots (7-day availability)  
   - Cancel or reschedule appointments  
   - Receive appointment confirmations and reminders  

3. **Patient Profile & Records**
   - Manage personal details  
   - View past and upcoming appointments  
   - Access basic medical record summaries (linked to Odoo EMR)  

---

### For Doctors (via EMR integration)
1. **Appointment Handling**
   - View and confirm upcoming appointments  
   - Mark appointments as completed or cancelled  
   - Manage availability status via Odoo EMR  

2. **Medical Record Access**
   - Integrated with EMR for patient history  
   - Update visit details directly into the EMR  

---

## Technical Implementation

### Frontend
- **React.js** with React Router for navigation  
- **Tailwind CSS** for responsive UI  
- **Toast notifications** for user feedback  
- **Context API** for state management  

### Backend
- **FastAPI** (Python) for REST API  
- **Odoo EMR** integration for medical records & scheduling  
- **PostgreSQL** (via Odoo) as the main database  
- **JWT authentication** for secure login  

---

## Key Components
1. **Authentication**
   - Secure login for patients  
   - JWT-based authentication and authorization  
   - Protected API endpoints  

2. **Appointment System**
   - Real-time slot availability sync with Odoo  
   - Prevents double-booking conflicts  
   - Tracks appointment statuses: *pending, confirmed, completed, cancelled*  

3. **Database Schema**
   - Patient profiles  
   - Doctor profiles (via EMR)  
   - Appointment records  
   - Availability slots  

---

## Getting Started

### Prerequisites
- Node.js (for frontend)  
- Python 3.11+ (for FastAPI backend)  
- PostgreSQL + Odoo (for EMR database)  
- npm or yarn  

### Installation
1. Clone the repository:  
   ```bash
   git clone https://github.com/yourusername/umcemr.git
   cd umcemr
   ```

2. Install dependencies:  
   ```bash
   # Frontend
   cd frontend
   npm install

   # Backend
   cd ../backend
   pip install -r requirements.txt
   ```

3. Configure environment variables:  
   - Create `.env` files in `frontend/` and `backend/`  
   - Define API keys, database URL, and JWT secrets  

4. Run the project:  
   ```bash
   # Start backend
   cd backend
   uvicorn main:app --reload

   # Start frontend
   cd frontend
   npm run dev
   ```

---

## Security Features
- Password hashing with **bcrypt**  
- **JWT token-based authentication**  
- Enforced HTTPS (with SSL via Nginx/Contabo)  
- Input validation and sanitization  
- Role-based access control (patients vs doctors/admins)  

---

## Contributing
This is a final year project, but contributions and suggestions are welcome!  
Please feel free to fork the repo and submit a Pull Request.  

---

## License
This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.  
