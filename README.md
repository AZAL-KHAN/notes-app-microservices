## 🚀 About the Application

📝 **Notes App – Microservices Architecture**

Notes App Microservices is a simple and scalable notes application built using **Python Flask** and **MySQL**, designed with a **microservices-based architecture**.

### 🔧 Tech Stack
- 🐍 Python Flask – Backend services  
- 🐬 MySQL – Database  
- 🐳 Docker & Docker Compose – Containerization  

---

### 🧩 Microservices Overview
The application consists of **4 independent microservices**, each with a clear responsibility:

1️⃣ **🔐 Login Service**  
Handles user authentication (signup & login) securely.

2️⃣ **🎨 Frontend Service**  
Provides the user interface to interact with the application.

3️⃣ **⚙️ Backend Service**  
Handles creating, viewing, and managing notes.

4️⃣ **🗄️ Database Service (MySQL)**  
Stores user data and notes persistently.

### ✨ Key Highlights
- 📦 Fully containerized using Docker  
- 🔁 Services communicate via APIs  
- 📈 Easy to scale and extend  
- 🛠️ Ideal for learning **DevOps & Microservices**

---
---

▶️ How to Run the Application (Using Docker)

This application is fully Dockerized, so you don’t need to install Python or MySQL locally.
Make sure you have Docker and Docker Compose installed on your system.

🔧 Prerequisites

🐳 Docker (version 20+ recommended)

🧩 Docker Compose

You can verify installation using:

```
docker --version
docker compose version
```

---

🚀 Steps to Run the App

1️⃣ Clone the repository
```
git clone https://github.com/AZAL-KHAN/notes-app-microservices.git
cd notes-app-microservices
```

2️⃣ Start all services using Docker Compose
```
docker compose up --build
```
This command will:

- Build images for all microservices

- Start the Login, Frontend, Backend, and MySQL services

- Set up networking between containers

3️⃣ Access the application

- Open your browser and go to:
  ```
  http://localhost:8080
  ```

---


🧪 How to Use the App

- 🔐 Enter your email address and password on the login page

- ▶️ Click the Login button to continue

- 📝 After successful login, you will be redirected to the Notes page

- ✍️ Create, view, and manage your personal notes

- 🔒 Notes are accessible only to the logged-in user

---

 ⏹️ Stop the Application

To stop all running containers:
```
docker compose down
```

---

💡 Notes

All services run in isolated containers

MySQL data is managed by Docker volumes

Ideal setup for learning Docker, Microservices, and DevOps workflows
