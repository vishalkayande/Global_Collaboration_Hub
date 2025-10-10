from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from database import db, User, Workspace, Membership, Message, File, Task, Project, JoinRequest, ProjectSubmission, ProjectReview, PasswordReset
from sqlalchemy import text
from config import Config

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
jwt = JWTManager(app)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# JWT configuration - using default behavior

# Create tables
with app.app_context():
    db.create_all()
    # Lightweight migration for SQLite: ensure new user profile columns exist
    try:
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        if db_uri.startswith('sqlite'):
            existing_cols = [row[1] for row in db.session.execute(text("PRAGMA table_info('users');")).fetchall()]
            alter_statements = []
            if 'role' not in existing_cols:
                alter_statements.append("ALTER TABLE users ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'student';")
            if 'domain' not in existing_cols:
                alter_statements.append("ALTER TABLE users ADD COLUMN domain VARCHAR(120);")
            if 'skills' not in existing_cols:
                alter_statements.append("ALTER TABLE users ADD COLUMN skills TEXT;")
            if 'experience_years' not in existing_cols:
                alter_statements.append("ALTER TABLE users ADD COLUMN experience_years INTEGER;")
            if 'portfolio_link' not in existing_cols:
                alter_statements.append("ALTER TABLE users ADD COLUMN portfolio_link VARCHAR(255);")
            if 'resume_link' not in existing_cols:
                alter_statements.append("ALTER TABLE users ADD COLUMN resume_link VARCHAR(255);")
            for stmt in alter_statements:
                db.session.execute(text(stmt))
            if alter_statements:
                db.session.commit()
    except Exception:
        db.session.rollback()

# Import routes
from routes import api

# Register blueprint
app.register_blueprint(api)

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'Global Collaboration Hub API is running',
        'timestamp': datetime.utcnow().isoformat()
    }), 200

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'error': 'Method not allowed'}), 405

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    db.session.rollback()
    return jsonify({'error': 'An unexpected error occurred'}), 500

# Authentication routes
@app.route('/api/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json() or {}
        
        # Validate required fields
        required_fields = ['username', 'email', 'password', 'first_name', 'last_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        # Validate role
        role = data.get('role', 'student')
        if role not in ['student', 'admin', 'external']:
            return jsonify({'error': 'Invalid role'}), 400
        
        # Validate email format
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, data['email']):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Validate password strength
        if len(data['password']) < 6:
            return jsonify({'error': 'Password must be at least 6 characters long'}), 400
        
        # Check if user already exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already taken'}), 400
        
        # Create new user
        user = User(
            username=data['username'],
            email=data['email'],
            password_hash=generate_password_hash(data['password']),
            first_name=data['first_name'],
            last_name=data['last_name'],
            role=role
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Create access token
        access_token = create_access_token(identity=str(user.id))
        
        return jsonify({
            'message': 'User created successfully',
            'access_token': access_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        user = User.query.filter_by(email=data['email']).first()
        
        if user and check_password_hash(user.password_hash, data['password']):
            access_token = create_access_token(identity=str(user.id))
            return jsonify({
                'message': 'Login successful',
                'access_token': access_token,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': user.role
                }
            }), 200
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/logout', methods=['POST'])
@jwt_required()
def logout():
    return jsonify({'message': 'Logout successful'}), 200

# Forgot password endpoints
@app.route('/api/forgot-password', methods=['POST'])
def forgot_password():
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'error': 'Email not found'}), 404
        
        # Generate reset token
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=1)
        
        # Create password reset record
        reset_record = PasswordReset(
            user_id=user.id,
            token=token,
            expires_at=expires_at
        )
        
        db.session.add(reset_record)
        db.session.commit()
        
        # Send email (simplified - in production use proper email service)
        try:
            send_reset_email(user.email, token)
            return jsonify({'message': 'Password reset email sent'}), 200
        except Exception as e:
            return jsonify({'error': 'Failed to send email'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reset-password', methods=['POST'])
def reset_password():
    try:
        data = request.get_json()
        token = data.get('token')
        new_password = data.get('password')
        
        if not token or not new_password:
            return jsonify({'error': 'Token and password are required'}), 400
        
        if len(new_password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters long'}), 400
        
        # Find valid reset record
        reset_record = PasswordReset.query.filter_by(
            token=token, 
            used=False
        ).first()
        
        if not reset_record:
            return jsonify({'error': 'Invalid or expired token'}), 400
        
        if reset_record.expires_at < datetime.utcnow():
            return jsonify({'error': 'Token has expired'}), 400
        
        # Update user password
        user = User.query.get(reset_record.user_id)
        user.password_hash = generate_password_hash(new_password)
        
        # Mark token as used
        reset_record.used = True
        
        db.session.commit()
        
        return jsonify({'message': 'Password updated successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def send_reset_email(email, token):
    """Send password reset email (simplified implementation)"""
    # In production, use proper email service like SendGrid, AWS SES, etc.
    reset_url = f"http://localhost:3000/reset-password.html?token={token}"
    
    msg = MIMEMultipart()
    msg['From'] = "noreply@collaborationhub.com"
    msg['To'] = email
    msg['Subject'] = "Password Reset Request"
    
    body = f"""
    You requested a password reset for your Global Collaboration Hub account.
    
    Click the link below to reset your password:
    {reset_url}
    
    This link will expire in 1 hour.
    
    If you didn't request this reset, please ignore this email.
    """
    
    msg.attach(MIMEText(body, 'plain'))
    
    # For development, just print the reset URL
    print(f"Password reset URL for {email}: {reset_url}")
    
    # In production, uncomment and configure SMTP:
    # server = smtplib.SMTP('smtp.gmail.com', 587)
    # server.starttls()
    # server.login("your-email@gmail.com", "your-password")
    # server.send_message(msg)
    # server.quit()

# User profile routes
@app.route('/api/profile', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role,
            'profile_picture': user.profile_picture,
            'bio': user.bio,
            'domain': user.domain,
            'skills': user.skills,
            'experience_years': user.experience_years,
            'portfolio_link': user.portfolio_link,
            'resume_link': user.resume_link,
            'created_at': user.created_at.isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Update user fields
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'bio' in data:
            user.bio = data['bio']
        if 'profile_picture' in data:
            user.profile_picture = data['profile_picture']
        # Extended profile
        if 'domain' in data:
            user.domain = data['domain']
        if 'skills' in data:
            user.skills = data['skills']
        if 'experience_years' in data:
            try:
                user.experience_years = int(data['experience_years']) if data['experience_years'] is not None else None
            except ValueError:
                return jsonify({'error': 'experience_years must be a number'}), 400
        if 'portfolio_link' in data:
            user.portfolio_link = data['portfolio_link']
        if 'resume_link' in data:
            user.resume_link = data['resume_link']
        
        db.session.commit()
        
        return jsonify({'message': 'Profile updated successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Workspace routes
@app.route('/api/workspaces', methods=['GET'])
@jwt_required()
def get_workspaces():
    try:
        user_id = int(get_jwt_identity())
        
        # Get workspaces where user is an accepted member
        memberships = Membership.query.filter_by(user_id=user_id, status='accepted').all()
        workspaces = []
        
        for membership in memberships:
            workspace = Workspace.query.get(membership.workspace_id)
            if workspace:
                workspaces.append({
                    'id': workspace.id,
                    'name': workspace.name,
                    'description': workspace.description,
                    'role': membership.role,
                    'status': membership.status,
                    'created_at': workspace.created_at.isoformat()
                })
        
        return jsonify(workspaces), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/workspaces', methods=['POST'])
@jwt_required()
def create_workspace():
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        # Create workspace
        workspace = Workspace(
            name=data['name'],
            description=data.get('description', ''),
            created_by=user_id
        )
        
        db.session.add(workspace)
        db.session.flush()  # Get the workspace ID
        
        # Add creator as owner with accepted status
        membership = Membership(
            user_id=user_id,
            workspace_id=workspace.id,
            role='owner',
            status='accepted',
            joined_at=datetime.utcnow()
        )
        
        db.session.add(membership)
        db.session.commit()
        
        return jsonify({
            'message': 'Workspace created successfully',
            'workspace': {
                'id': workspace.id,
                'name': workspace.name,
                'description': workspace.description,
                'role': 'owner'
            }
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Message routes
@app.route('/api/workspaces/<int:workspace_id>/messages', methods=['GET'])
@jwt_required()
def get_messages(workspace_id):
    try:
        user_id = int(get_jwt_identity())
        
        # Check if user is accepted member of workspace
        membership = Membership.query.filter_by(user_id=user_id, workspace_id=workspace_id, status='accepted').first()
        if not membership:
            return jsonify({'error': 'Access denied'}), 403
        
        # Get messages
        messages = Message.query.filter_by(workspace_id=workspace_id).order_by(Message.created_at.desc()).limit(50).all()
        
        message_list = []
        for message in messages:
            user = User.query.get(message.user_id)
            message_list.append({
                'id': message.id,
                'content': message.content,
                'message_type': message.message_type,
                'file_path': message.file_path,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                },
                'created_at': message.created_at.isoformat()
            })
        
        return jsonify(message_list[::-1]), 200  # Reverse to show oldest first
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Socket.IO events for real-time chat
@socketio.on('join_workspace')
def on_join_workspace(data):
    workspace_id = data.get('workspace_id')
    user_id = data.get('user_id')
    if not workspace_id or not user_id:
        emit('error', {'msg': 'Missing workspace_id or user_id'})
        return
    # Check if user is member of workspace
    membership = Membership.query.filter_by(user_id=user_id, workspace_id=workspace_id).first()
    if membership:
        join_room(f'workspace_{workspace_id}')
        emit('status', {'msg': f'Joined workspace {workspace_id}'})
    else:
        emit('error', {'msg': 'Access denied'})

@socketio.on('leave_workspace')
def on_leave_workspace(data):
    workspace_id = data.get('workspace_id')
    if not workspace_id:
        emit('error', {'msg': 'Missing workspace_id'})
        return
    leave_room(f'workspace_{workspace_id}')
    emit('status', {'msg': f'Left workspace {workspace_id}'})

@socketio.on('send_message')
def handle_message(data):
    try:
        user_id = data.get('user_id')
        workspace_id = data.get('workspace_id')
        content = data.get('content')
        if not user_id or not workspace_id or not content:
            emit('error', {'msg': 'Missing required fields'})
            return
        
        # Check if user is member of workspace
        membership = Membership.query.filter_by(user_id=user_id, workspace_id=workspace_id).first()
        if not membership:
            emit('error', {'msg': 'Access denied'})
            return
        
        # Create message
        message = Message(
            workspace_id=workspace_id,
            user_id=user_id,
            content=content
        )
        
        db.session.add(message)
        db.session.commit()
        
        # Get user info
        user = User.query.get(user_id)
        
        # Emit to all users in the workspace
        emit('new_message', {
            'id': message.id,
            'content': message.content,
            'user': {
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name
            },
            'created_at': message.created_at.isoformat()
        }, room=f'workspace_{workspace_id}')
        
    except Exception as e:
        emit('error', {'msg': str(e)})

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)

