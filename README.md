# Photo Gallery Web App

A Django-based photo gallery web application with user authentication, profile management, photo browsing, tag filtering, and like/dislike interactions.

## Features

- User registration and authentication
- Profile management with bio and profile picture
- Photo gallery with grid display
- Tag-based photo filtering
- Photo detail view with like/dislike functionality
- Responsive design with Tailwind CSS

## Tech Stack

- Python 3.x, Django 6.x
- Tailwind CSS (via CDN)
- PostgreSQL (production) / SQLite (development)
- Pillow for image processing

## Setup

1. Clone the repository:
   ```
   git clone <repo-url>
   cd photo_gallery
   ```

2. Create and activate a virtual environment:
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```
   pip install django psycopg2-binary pillow
   ```

4. Configure environment variables (optional):
   ```
   export DB_ENGINE=django.db.backends.postgresql
   export DB_NAME=photo_gallery
   export DB_USER=postgres
   export DB_PASSWORD=yourpassword
   export DB_HOST=localhost
   export DB_PORT=5432
   ```

5. Run migrations:
   ```
   python manage.py migrate
   ```

6. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

7. Run the development server:
   ```
   python manage.py runserver
   ```

8. Access the app at `http://127.0.0.1:8000`

## Admin Panel

Access the admin interface at `/admin/` to manage users, photos, tags, and interactions.

## Deployment (Render)

1. Push to a Git repository.
2. On Render, create a new Web Service linked to your repo.
3. Set the build command: `pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput`
4. Set the start command: `gunicorn photo_gallery_project.wsgi`
5. Add environment variables for database and Django secret key.
6. Deploy.
