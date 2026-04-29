# Cooling System Monitoring Dashboard

A real-time dashboard to monitor machine sensor data such as temperature, humidity, and pressure. This project demonstrates how data flows from generation to visualization using Python, Flask, and a web-based frontend.

---

##  Features
- Real-time data generation using Python
- Data stored and updated in CSV format
- Flask-based backend API for data access
- Live dashboard with graphs using Chart.js
- Auto-refresh functionality for continuous updates
- Status monitoring (OK / WARNING / ERROR)

---

##   Project Architecture
This project consists of three main components:

1. Data Generator (Python)
   - Generates random sensor data every 5 seconds
   - Stores data in a CSV file

2. Backend (Flask API)
   - Reads CSV data using pandas
   - Provides API endpoints:
     - /all → returns all data
     - /latest → returns latest record

3. Frontend (HTML + JavaScript)
   - Displays sensor data and status
   - Uses Chart.js for live graphs
   - Fetches data from backend API
   - Auto-refresh every 5 seconds

---

## Tech Stack
- Python
- Flask
- Pandas
- CSV
- HTML
- JavaScript
- Chart.js

---

##  How to Run

1. Run the data generator:
   python generator.py

2. Start the backend server:
   python app.py

3. Run the frontend:
   python -m http.server 8080

4. Open in browser:
   http://localhost:8080

---

##  Customization
- Modify refresh time in frontend (default: 5 seconds)
- Add new sensor fields in generator and backend
- Change API URL if backend port changes

---

##   Learning Outcomes
- Understanding of basic backend development using Flask
- Working with CSV data and APIs
- Connecting backend with frontend
- Building real-time dashboards and data visualization

---

## 🔗 Author
Prince Pandey
