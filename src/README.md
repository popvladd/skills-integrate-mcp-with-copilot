# Mergington High School Activities API

A super simple FastAPI application that allows students to view extracurricular activities and teachers to manage enrollment.

## Features

- View all available extracurricular activities
- Teacher-only sign-up and unregister controls
- Public activity and participant lists

## Getting Started

1. From the repository root, install the dependencies:

   ```
   pip install -r requirements.txt
   ```

2. Configure the teacher login and session signing secret in the environment:

   ```
   export TEACHER_USERNAME=teacher
   export TEACHER_PASSWORD='use-a-unique-password'
   export SESSION_SECRET="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
   ```

   Keep these values out of source control. For production, set `SESSION_COOKIE_SECURE=true` and serve the app over HTTPS.

3. Run the application from the `src` directory:

   ```
   cd src
   uvicorn app:app --host 0.0.0.0 --port 8000
   ```

4. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/activities`                                                     | Get all activities with their details and current participant count |
| POST   | `/auth/login`                                                     | Start a teacher session                                              |
| GET    | `/auth/session`                                                   | Check the current session                                            |
| POST   | `/auth/logout`                                                    | End the current teacher session                                      |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Teacher-only sign up                                                 |
| DELETE | `/activities/{activity_name}/unregister?email=student@mergington.edu` | Teacher-only unregister                                          |

## Data Model

The application uses a simple data model with meaningful identifiers:

1. **Activities** - Uses activity name as identifier:

   - Description
   - Schedule
   - Maximum number of participants allowed
   - List of student emails who are signed up

2. **Students** - Uses email as identifier:
   - Name
   - Grade level

All data is stored in memory, which means data will be reset when the server restarts.
