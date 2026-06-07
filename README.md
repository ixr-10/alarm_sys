# alarm_sys
## Requirements
- Python 3.11+
- MySQL 8.0
- Redis (https://github.com/tporadowski/redis/releases)
- Docker (for test server)

## Setup Steps

### 1. Clone the repo
git clone <your-repo-url>
cd alarm_sys/back-end

### 2. Create virtual environment
python -m venv venv
venv\Scripts\activate

### 3. Install dependencies
pip install -r requirements.txt

### 4. Create .env file
Copy .env.example and fill in your MySQL password:
DB_NAME=server_monitor_db
DB_USER=root
DB_PASSWORD=your_password_here
DB_HOST=localhost
DB_PORT=3306
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=django-insecure-change-this-123456

### 5. Create MySQL database
Open MySQL Workbench and run:
CREATE DATABASE server_monitor_db;

### 6. Run migrations
python manage.py migrate
python manage.py createsuperuser

### 7. Start test server (Docker)
docker run -d --name test-server -p 2222:22 rastasheep/ubuntu-sshd:18.04

### 8. Run everything (4 terminals)
# Terminal 1
python manage.py runserver

# Terminal 2
celery -A core worker --loglevel=info --pool=solo

# Terminal 3
celery -A core beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler

# Terminal 4
redis-cli ping  (just to verify Redis is running)

### 9. Add test server in admin
Go to http://127.0.0.1:8000/admin
Add server:
- IP: 127.0.0.1
- Port: 2222
- User: root
- Password: root