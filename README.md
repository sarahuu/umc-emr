# Prescripto - Doctor Appointment Booking System

Prescripto is a modern web application that facilitates seamless doctor appointment booking between patients and healthcare providers. The system is built with a React frontend and Node.js backend, providing a user-friendly interface for both patients and doctors.

## Features

### For Patients
1. **Doctor Search and Discovery**
   - Browse through a list of doctors by specialty
   - View detailed doctor profiles including qualifications, experience, and fees
   - Filter doctors based on availability and specialization

2. **Appointment Management**
   - Book appointments with preferred doctors
   - View available time slots for the next 7 days
   - Cancel or reschedule appointments
   - Track appointment history
   - Receive appointment confirmations

3. **User Profile Management**
   - Create and manage personal profiles
   - View appointment history
   - Update personal information
   - Track medical records

### For Doctors
1. **Appointment Management**
   - View and manage upcoming appointments
   - Mark appointments as completed
   - Cancel appointments when necessary
   - Set availability status

2. **Profile Management**
   - Create and maintain professional profiles
   - Update qualifications and experience
   - Set consultation fees
   - Manage availability schedule

3. **Dashboard**
   - View appointment statistics
   - Track patient history
   - Monitor daily/weekly schedules
   - Manage appointment statuses

## Technical Implementation

### Frontend
- Built with React.js
- Uses React Router for navigation
- Implements responsive design with Tailwind CSS
- Features toast notifications for user feedback
- Context API for state management

### Backend
- Node.js with Express.js
- MongoDB for database management
- JWT for authentication
- RESTful API architecture

### Key Components
1. **Authentication System**
   - Secure login for both patients and doctors
   - JWT-based authentication
   - Protected routes and API endpoints

2. **Appointment System**
   - Real-time slot availability checking
   - 30-minute appointment slots
   - Conflict prevention for double bookings
   - Appointment status tracking (pending, completed, cancelled)

3. **Database Schema**
   - User profiles
   - Doctor profiles
   - Appointment records
   - Slot management

## Getting Started

### Prerequisites
- Node.js
- MongoDB
- npm or yarn

### Installation
1. Clone the repository
2. Install dependencies:
   ```bash
   # Install frontend dependencies
   cd frontend
   npm install

   # Install backend dependencies
   cd ../backend
   npm install
   ```

3. Set up environment variables:
   - Create `.env` files in both frontend and backend directories
   - Configure necessary environment variables

4. Start the development servers:
   ```bash
   # Start backend server
   cd backend
   npm run dev

   # Start frontend server
   cd frontend
   npm run dev
   ```

## Security Features
- Password encryption using bcrypt
- JWT token-based authentication
- Protected API endpoints
- Input validation and sanitization

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License - see the LICENSE file for details. 