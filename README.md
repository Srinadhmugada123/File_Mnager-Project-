File Manager Project
📌 About

The File Manager is a backend application built with Python and Django that allows users to organize files and folders with advanced features such as hierarchical folder structures, file versioning, and permission control. It uses REST APIs for communication and supports JWT Authentication for secure access.

The system ensures files are never permanently deleted — instead, multiple versions are maintained so users can track history (v1, v2, etc.) whenever a file is modified. Permissions (read/write) are also managed to provide secure collaboration between users.

This project demonstrates strong knowledge of Django REST Framework (DRF), JWT authentication, file storage logic, and API testing with Postman.

✨ Features

📁 Folder & Subfolder hierarchy (nested folder structure)

🗂 File storage inside folders/subfolders

🔐 JWT Authentication for secure access

📜 File versioning (track history: v1, v2, etc., old versions not deleted)

📝 Permissions (read, write access per file/folder)

🧑‍💻 Created by / Updated by tracking for accountability

🛠 Tested using Postman

🛠 Tech Stack

Language: Python

Framework: Django (Django REST Framework for APIs)

Database: Default SQLite (can be switched to PostgreSQL/MySQL)

Authentication: JWT Authentication

Version Control: Git & GitHub

Testing Tools: Postman

IDE: Visual Studio Code

🚀 Installation & Setup
Prerequisites

Git

Python 3.8+

pip

(Optional) Virtualenv/venv

Steps

Clone the repo

git clone https://github.com/<your-username>/file_manager.git
cd file_manager


Create and activate a virtual environment

# Windows
python -m venv venv
.\venv\Scripts\Activate.ps1

# macOS/Linux
python3 -m venv venv
source venv/bin/activate


Install dependencies

pip install -r requirements.txt


Run migrations

python manage.py migrate


Create a superuser (admin account)

python manage.py createsuperuser


Run the development server

python manage.py runserver


Access API endpoints

API Root → http://127.0.0.1:8000/api/

JWT Auth → http://127.0.0.1:8000/api/token/ (get access & refresh token)

🔑 Authentication (JWT)

Obtain a JWT token:

POST http://127.0.0.1:8000/api/token/
{
  "username": "your_username",
  "password": "your_password"
}


Include it in headers:

Authorization: Bearer <your-access-token>

🎯 Usage Examples
1️⃣ Create Folder
POST /api/folders/
{
  "name": "Projects",
  "parent": null
}

2️⃣ Create Subfolder
POST /api/folders/
{
  "name": "Django",
  "parent": 1
}

3️⃣ Upload File
POST /api/files/
{
  "folder": 2,
  "file": "<binary-file>",
  "permissions": "write"
}

4️⃣ Update File (creates new version v2, v3, etc.)
PUT /api/files/5/
{
  "file": "<modified-binary-file>"
}

5️⃣ Get File History (all versions)
GET /api/files/5/versions/

📂 Project Structure
FILE_MANAGER/
├── core/               # Django app (folders, files, permissions, APIs live here)
├── file_manager/       # Django project settings (settings.py, urls.py, wsgi.py, asgi.py)
├── media/              # Uploaded files stored here
├── manage.py           # Django project runner



👤 Author

Mugada Srinadh

GitHub: Srinadhmugada123
