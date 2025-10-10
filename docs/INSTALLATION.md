# Installation Guide

This guide will help you set up the Global Collaboration Hub on your local machine.

## Prerequisites

Before installing the Global Collaboration Hub, ensure you have the following software installed:

### Required Software

1. **Python 3.8 or higher**
   - Download from: https://www.python.org/downloads/
   - Make sure to check "Add Python to PATH" during installation

2. **MySQL 8.0 or higher**
   - Download from: https://dev.mysql.com/downloads/mysql/
   - Remember the root password you set during installation

3. **Git** (optional, for version control)
   - Download from: https://git-scm.com/downloads

## Quick Setup

### Option 1: Automated Setup (Recommended)

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd NGO_COLLAB
   ```

2. **Run the setup script**
   ```bash
   python setup.py
   ```

3. **Start the backend server**
   ```bash
   python run_backend.py
   ```

4. **Open the frontend**
   - Open `frontend/index.html` in your web browser
   - Or use a local server: `python -m http.server 8000` in the frontend directory

### Option 2: Manual Setup

#### 1. Database Setup

1. **Start MySQL service**
   - Windows: Start MySQL from Services or Command Prompt
   - macOS: `brew services start mysql`
   - Linux: `sudo systemctl start mysql`

2. **Create the database**
   ```bash
   mysql -u root -p < database/schema.sql
   ```

#### 2. Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Create environment file**
   Create `backend/.env` with the following content:
   ```
   DATABASE_URL=mysql+pymysql://root:your_password@localhost/global_collab_hub
   SECRET_KEY=your-secret-key-change-in-production
   JWT_SECRET_KEY=jwt-secret-string-change-in-production
   FLASK_ENV=development
   FLASK_DEBUG=True
   ```

6. **Start the backend server**
   ```bash
   python app.py
   ```

#### 3. Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Open in browser**
   - Simply open `index.html` in your web browser
   - Or use a local server: `python -m http.server 8000`

## Configuration

### Database Configuration

Update the database connection in `backend/.env`:

```env
DATABASE_URL=mysql+pymysql://username:password@localhost/global_collab_hub
```

### Security Configuration

**IMPORTANT**: Change the following keys in production:

```env
SECRET_KEY=your-unique-secret-key-here
JWT_SECRET_KEY=your-unique-jwt-secret-here
```

### File Upload Configuration

The application supports file uploads up to 16MB. To change this limit, modify `backend/config.py`:

```python
MAX_CONTENT_LENGTH = 32 * 1024 * 1024  # 32MB
```

## Troubleshooting

### Common Issues

1. **MySQL Connection Error**
   - Ensure MySQL is running
   - Check username and password in `.env`
   - Verify database exists: `mysql -u root -p -e "SHOW DATABASES;"`

2. **Python Module Not Found**
   - Ensure virtual environment is activated
   - Reinstall requirements: `pip install -r requirements.txt`

3. **Port Already in Use**
   - Change port in `backend/app.py`: `socketio.run(app, debug=True, host='0.0.0.0', port=5001)`
   - Update frontend API URL in `frontend/app.js`

4. **CORS Errors**
   - Ensure backend is running on the correct port
   - Check API_BASE_URL in `frontend/app.js`

### Logs and Debugging

- Backend logs are displayed in the terminal where you run `python app.py`
- Check browser console (F12) for frontend errors
- Enable debug mode by setting `FLASK_DEBUG=True` in `.env`

## Production Deployment

### Security Checklist

- [ ] Change default secret keys
- [ ] Use environment variables for sensitive data
- [ ] Enable HTTPS
- [ ] Configure proper CORS settings
- [ ] Set up proper file upload restrictions
- [ ] Use a production WSGI server (e.g., Gunicorn)

### Database Security

- [ ] Create dedicated database user (not root)
- [ ] Use strong passwords
- [ ] Enable SSL connections
- [ ] Regular backups

### Server Configuration

- [ ] Use reverse proxy (Nginx)
- [ ] Configure firewall rules
- [ ] Set up SSL certificates
- [ ] Monitor server resources

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review the logs for error messages
3. Ensure all prerequisites are installed correctly
4. Verify database connection and permissions

For additional help, please refer to the project documentation or create an issue in the repository.
