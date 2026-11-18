# TimeTracker (IM2 Project - Phase 1)

**TimeTracker** is a web-based attendance and leave management system designed to modernize how schools and small organizations handle employee attendance. It replaces manual paper logbooks and outdated card systems with a reliable digital solution that eliminates buddy-punching and human error.

## Technology Stack
- **Backend & Frontend:** Full Stack Django (Python 3.15) with Django Templates
- **Styling:** Bootstrap 5, Bootstrap Icons, Custom CSS
- **Database:** PostgreSQL / Supabase (configured via `dj-database-url` and `psycopg`)
- **Authentication:** Django Built-in Authentication with Custom User Model (`CustomUser`)

---

## Phase 1: Account Feature Implementation

### 1. Account Registration
- User registration with validation: required fields, unique username, unique and valid email, matching password confirmation.
- Password hashing using Django's built-in secure password management (`PBKDF2SHA256`).
- Role assignment (`Administrator` or `Employee`).
- Success and error feedback using the Django messages framework.

### 2. Login / Logout
- Secure authentication supporting username and email login.
- Feedback on invalid credentials.
- Safe logout terminating active sessions.
- View protection with `@login_required` (redirects unauthenticated users to `/accounts/login/`).

### 3. Role-Based User Dashboards
- Separate dashboards for **Administrator** and **Employee**:
  - **Admin Dashboard (`/accounts/dashboard/admin/`)**: Overview metrics, staff attendance management, leave approval queues, payroll-ready reporting shortcuts.
  - **Employee Dashboard (`/accounts/dashboard/employee/`)**: Clock in/out interface preview, personal attendance history, leave request status, profile shortcut.
- Access control decorator (`@role_required`) prevents cross-role URL tampering (e.g., employees cannot access the admin dashboard).

### 4. User Profile
- View profile details (`/accounts/profile/`).
- Update profile information (`/accounts/profile/edit/`), including first name, last name, email, contact number, department, and profile photo.
- Strict isolation: users can only view and edit their own profile.

---

## Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/sairaarias/TimeTracker-Arias-SairaMariz-G7.git
cd TimeTracker-Arias-SairaMariz-G7
```

### 2. Set Up Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Update your database configuration in `.env` with your **Supabase** or **PostgreSQL** connection string:
```env
SECRET_KEY=your-django-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres
```

### 5. Run Migrations & Create Superuser
```bash
python manage.py makemigrations accounts
python manage.py migrate
python manage.py createsuperuser
```

### 6. Run the Development Server
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000/` in your browser.
