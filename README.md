# Web Application Exercise

A little exercise to build a web application following an agile development process. See the [instructions](instructions.md) for more detail.

## Product vision statement

A mobile friendly app that helps travelers find compatible travel partners based on their personal preferences and traveling habits which fosters a new way to meet friends and emphasize traveling safely.

## User stories 

https://github.com/software-students-spring2025/2-web-app-diet-coke/issues/


## Steps necessary to run the software

### Prerequisites
- Python 3.8 or higher
- MongoDB (local installation or MongoDB Atlas account)
- Git

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Set up a virtual environment**
   - On Windows/macOS:
     ```bash
     python -m venv venv
     ```
   - On Ubuntu/Debian WSL systems:
     ```bash
     python3 -m venv venv
     ```
     Note: If you installed `python-is-python3` package, you can use `python` instead of `python3`.

3. **Activate the virtual environment**
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure environment variables**
   - Copy the example environment file:
     ```bash
     cp env.example .env
     ```
   - Edit the `.env` file with your specific configuration:
     - Set `MONGO_URI` to your MongoDB connection string
     - Set a secure `SECRET_KEY` for Flask session management

6. **Run the application**
   ```bash
   flask run
   ```
   The application will be available at http://127.0.0.1:5000/

## Task boards

https://github.com/orgs/software-students-spring2025/projects/56/views/1

https://github.com/orgs/software-students-spring2025/projects/70
