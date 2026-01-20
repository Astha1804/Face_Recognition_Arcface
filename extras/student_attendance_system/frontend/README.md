# Frontend - Student Attendance System

This folder contains the **React.js frontend** for the Student Attendance System,
which uses a face recognition backend powered by **ArcFace (InsightFace)**.

The frontend is responsible for:
- Capturing user input / webcam feed
- Sending data to the backend recognition API
- Displaying recognized student name and attendance status

---

# Tech Stack
- React.js (Create React App)
- JavaScript (ES6)
- HTML5 & CSS3
- Node.js & npm

---

# Folder Structure
frontend/
    public/
    src/
        App.js
        App.css
        index.js
    package.json
    README.md

---

# How to Run the Frontend

Make sure **Node.js** is installed.

```bash
npm install
npm start

# The application will run at:
http://localhost:3000

---

# Backend Dependency

This frontend depends on a Python backend that performs face recognition and
attendance marking.
Please ensure the backend server is running before starting the frontend.

---

# Notes

node_modules is intentionally excluded from GitHub.
Configuration files can be updated as needed for backend API endpoints.

• Author
Astha Dubey