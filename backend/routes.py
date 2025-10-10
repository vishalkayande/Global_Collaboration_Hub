from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from database import db, User, Workspace, Membership, Message, File, Task, Project, JoinRequest, ProjectSubmission, ProjectReview
import os
import uuid
from datetime import datetime

# Create blueprint
api = Blueprint('api', __name__)

# File routes
@api.route('/api/workspaces/<int:workspace_id>/files', methods=['GET'])
@jwt_required()
def get_files(workspace_id):
    try:
        user_id = get_jwt_identity()
        
        # Check if user is accepted member of workspace
        membership = Membership.query.filter_by(user_id=user_id, workspace_id=workspace_id, status='accepted').first()
        if not membership:
            return jsonify({'error': 'Access denied'}), 403
        
        # Get files
        files = File.query.filter_by(workspace_id=workspace_id).order_by(File.created_at.desc()).all()
        
        file_list = []
        for file in files:
            uploader = User.query.get(file.uploaded_by)
            file_list.append({
                'id': file.id,
                'filename': file.filename,
                'original_filename': file.original_filename,
                'file_size': file.file_size,
                'file_type': file.file_type,
                'description': file.description,
                'uploaded_by': {
                    'id': uploader.id,
                    'username': uploader.username,
                    'first_name': uploader.first_name,
                    'last_name': uploader.last_name
                },
                'created_at': file.created_at.isoformat()
            })
        
        return jsonify(file_list), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/api/workspaces/<int:workspace_id>/files', methods=['POST'])
@jwt_required()
def upload_file(workspace_id):
    try:
        user_id = get_jwt_identity()
        
        # Check if user is accepted member of workspace
        membership = Membership.query.filter_by(user_id=user_id, workspace_id=workspace_id, status='accepted').first()
        if not membership:
            return jsonify({'error': 'Access denied'}), 403
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file:
            # Generate unique filename
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            
            # Create uploads directory if it doesn't exist
            upload_dir = os.path.join('uploads', f'workspace_{workspace_id}')
            os.makedirs(upload_dir, exist_ok=True)
            
            file_path = os.path.join(upload_dir, unique_filename)
            file.save(file_path)
            
            # Get file info
            file_size = os.path.getsize(file_path)
            file_type = file.content_type or 'application/octet-stream'
            
            # Save file record to database
            file_record = File(
                workspace_id=workspace_id,
                uploaded_by=user_id,
                filename=unique_filename,
                original_filename=filename,
                file_path=file_path,
                file_size=file_size,
                file_type=file_type,
                description=request.form.get('description', '')
            )
            
            db.session.add(file_record)
            db.session.commit()
            
            return jsonify({
                'message': 'File uploaded successfully',
                'file': {
                    'id': file_record.id,
                    'filename': file_record.filename,
                    'original_filename': file_record.original_filename,
                    'file_size': file_record.file_size,
                    'file_type': file_record.file_type
                }
            }), 201
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/api/files/<int:file_id>/download', methods=['GET'])
@jwt_required()
def download_file(file_id):
    try:
        user_id = get_jwt_identity()
        
        # Get file record
        file_record = File.query.get(file_id)
        if not file_record:
            return jsonify({'error': 'File not found'}), 404
        
        # Check if user is member of workspace
        membership = Membership.query.filter_by(user_id=user_id, workspace_id=file_record.workspace_id).first()
        if not membership:
            return jsonify({'error': 'Access denied'}), 403
        
        # Check if file exists
        if not os.path.exists(file_record.file_path):
            return jsonify({'error': 'File not found on server'}), 404
        
        return send_file(file_record.file_path, as_attachment=True, download_name=file_record.original_filename)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Task routes
@api.route('/api/workspaces/<int:workspace_id>/tasks', methods=['GET'])
@jwt_required()
def get_tasks(workspace_id):
    try:
        user_id = get_jwt_identity()
        
        # Check if user is accepted member of workspace
        membership = Membership.query.filter_by(user_id=user_id, workspace_id=workspace_id, status='accepted').first()
        if not membership:
            return jsonify({'error': 'Access denied'}), 403
        
        # Get tasks
        tasks = Task.query.filter_by(workspace_id=workspace_id).order_by(Task.created_at.desc()).all()
        
        task_list = []
        for task in tasks:
            creator = User.query.get(task.created_by)
            assignee = User.query.get(task.assigned_to) if task.assigned_to else None
            
            task_list.append({
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'status': task.status,
                'priority': task.priority,
                'due_date': task.due_date.isoformat() if task.due_date else None,
                'created_by': {
                    'id': creator.id,
                    'username': creator.username,
                    'first_name': creator.first_name,
                    'last_name': creator.last_name
                },
                'assigned_to': {
                    'id': assignee.id,
                    'username': assignee.username,
                    'first_name': assignee.first_name,
                    'last_name': assignee.last_name
                } if assignee else None,
                'created_at': task.created_at.isoformat()
            })
        
        return jsonify(task_list), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/api/workspaces/<int:workspace_id>/tasks', methods=['POST'])
@jwt_required()
def create_task(workspace_id):
    try:
        user_id = get_jwt_identity()
        
        # Check if user is accepted member of workspace
        membership = Membership.query.filter_by(user_id=user_id, workspace_id=workspace_id, status='accepted').first()
        if not membership:
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        
        # Parse due date if provided
        due_date = None
        if data.get('due_date'):
            due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
        
        # Create task
        task = Task(
            workspace_id=workspace_id,
            created_by=user_id,
            assigned_to=data.get('assigned_to'),
            title=data['title'],
            description=data.get('description', ''),
            priority=data.get('priority', 'medium'),
            due_date=due_date
        )
        
        db.session.add(task)
        db.session.commit()
        
        return jsonify({
            'message': 'Task created successfully',
            'task': {
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'status': task.status,
                'priority': task.priority,
                'due_date': task.due_date.isoformat() if task.due_date else None
            }
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/api/tasks/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    try:
        user_id = get_jwt_identity()
        
        # Get task
        task = Task.query.get(task_id)
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        # Check if user is member of workspace
        membership = Membership.query.filter_by(user_id=user_id, workspace_id=task.workspace_id).first()
        if not membership:
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        
        # Update task fields
        if 'title' in data:
            task.title = data['title']
        if 'description' in data:
            task.description = data['description']
        if 'status' in data:
            task.status = data['status']
        if 'priority' in data:
            task.priority = data['priority']
        if 'assigned_to' in data:
            task.assigned_to = data['assigned_to']
        if 'due_date' in data:
            task.due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00')) if data['due_date'] else None
        
        db.session.commit()
        
        return jsonify({'message': 'Task updated successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/api/tasks/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    try:
        user_id = get_jwt_identity()
        
        # Get task
        task = Task.query.get(task_id)
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        # Check if user is member of workspace
        membership = Membership.query.filter_by(user_id=user_id, workspace_id=task.workspace_id).first()
        if not membership:
            return jsonify({'error': 'Access denied'}), 403
        
        # Only creator or admin/owner can delete
        if task.created_by != user_id and membership.role not in ['owner', 'admin']:
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        db.session.delete(task)
        db.session.commit()
        
        return jsonify({'message': 'Task deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Profile discovery for agencies
@api.route('/api/students', methods=['GET'])
@jwt_required()
def list_students():
    try:
        current_id = get_jwt_identity()
        me = User.query.get(current_id)
        if me.role != 'external' and me.role != 'admin':
            return jsonify({'error': 'Insufficient permissions'}), 403
        q = User.query.filter_by(role='student').all()
        return jsonify([{
            'id': u.id,
            'first_name': u.first_name,
            'last_name': u.last_name,
            'email': u.email,
            'domain': u.domain,
            'skills': u.skills,
            'experience_years': u.experience_years,
            'portfolio_link': u.portfolio_link
        } for u in q]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/api/students/<int:student_id>', methods=['GET'])
@jwt_required()
def get_student(student_id):
    try:
        current_id = get_jwt_identity()
        me = User.query.get(current_id)
        if me.role != 'external' and me.role != 'admin':
            return jsonify({'error': 'Insufficient permissions'}), 403
        u = User.query.get(student_id)
        if not u or u.role != 'student':
            return jsonify({'error': 'Student not found'}), 404
        return jsonify({
            'id': u.id,
            'first_name': u.first_name,
            'last_name': u.last_name,
            'email': u.email,
            'domain': u.domain,
            'skills': u.skills,
            'experience_years': u.experience_years,
            'portfolio_link': u.portfolio_link,
            'resume_link': u.resume_link,
            'bio': u.bio
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Development convenience: allow switching own role (default enabled). In production, disable via ALLOW_ROLE_SWITCH=0
@api.route('/api/me/role', methods=['PUT'])
@jwt_required()
def switch_my_role():
    try:
        if os.getenv('ALLOW_ROLE_SWITCH', '1') != '1':
            return jsonify({'error': 'Role switching disabled'}), 403
        uid = get_jwt_identity()
        user = User.query.get(uid)
        data = request.get_json() or {}
        new_role = data.get('role')
        if new_role not in ['student', 'external', 'admin']:
            return jsonify({'error': 'Invalid role'}), 400
        user.role = new_role
        db.session.commit()
        return jsonify({'message': 'Role updated', 'role': user.role}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Join Request flow
@api.route('/api/requests', methods=['POST'])
@jwt_required()
def create_request():
    try:
        user_id = get_jwt_identity()
        me = User.query.get(user_id)
        if me.role != 'external' and me.role != 'admin':
            return jsonify({'error': 'Only external agencies or admin can send requests'}), 403
        data = request.get_json()
        req = JoinRequest(
            from_agency_id=user_id,
            to_student_id=data['to_student_id'],
            project_id=data.get('project_id'),
            workspace_id=data.get('workspace_id'),
            message=data.get('message', '')
        )
        db.session.add(req)
        db.session.commit()
        return jsonify({'message': 'Request sent', 'id': req.id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/api/requests', methods=['GET'])
@jwt_required()
def list_requests():
    try:
        user_id = get_jwt_identity()
        me = User.query.get(user_id)
        if me.role == 'student':
            rs = JoinRequest.query.filter_by(to_student_id=user_id).all()
        elif me.role in ['external', 'admin']:
            # External/Admin see all join requests
            rs = JoinRequest.query.order_by(JoinRequest.created_at.desc()).all()
        else:
            rs = []
        def serialize(r):
            return {
                'id': r.id,
                'from_agency_id': r.from_agency_id,
                'to_student_id': r.to_student_id,
                'project_id': r.project_id,
                'workspace_id': r.workspace_id,
                'message': r.message,
                'status': r.status,
                'created_at': r.created_at.isoformat()
            }
        return jsonify([serialize(r) for r in rs]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/api/requests/<int:req_id>/respond', methods=['POST'])
@jwt_required()
def respond_request(req_id):
    try:
        user_id = get_jwt_identity()
        req = JoinRequest.query.get(req_id)
        if not req:
            return jsonify({'error': 'Request not found'}), 404
        if req.to_student_id != user_id:
            return jsonify({'error': 'Insufficient permissions'}), 403
        data = request.get_json()
        action = data.get('action')  # 'accept' or 'reject'
        if action == 'accept':
            req.status = 'accepted'
            # If workspace provided, add membership
            if req.workspace_id:
                existing = Membership.query.filter_by(user_id=user_id, workspace_id=req.workspace_id).first()
                if not existing:
                    db.session.add(Membership(user_id=user_id, workspace_id=req.workspace_id, role='member'))
        elif action == 'reject':
            req.status = 'rejected'
        else:
            return jsonify({'error': 'Invalid action'}), 400
        db.session.commit()
        return jsonify({'message': 'Response recorded', 'status': req.status}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Projects and review
@api.route('/api/projects', methods=['POST'])
@jwt_required()
def create_project():
    try:
        uid = get_jwt_identity()
        me = User.query.get(uid)
        if me.role not in ['external', 'admin']:
            return jsonify({'error': 'Only external agency or admin can create projects'}), 403
        data = request.get_json()
        ws_id = data.get('workspace_id')
        if not ws_id:
            return jsonify({'error': 'workspace_id is required'}), 400
        # Ensure creator is member (owner/admin) of the workspace
        membership = Membership.query.filter_by(user_id=uid, workspace_id=ws_id).first()
        if not membership or membership.role not in ['owner', 'admin']:
            return jsonify({'error': 'You must be owner/admin of the workspace'}), 403
        p = Project(title=data['title'], description=data.get('description',''), created_by=uid, workspace_id=ws_id)
        db.session.add(p)
        db.session.commit()
        return jsonify({'message': 'Project created', 'id': p.id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/api/projects', methods=['GET'])
@jwt_required()
def list_projects():
    try:
        uid = get_jwt_identity()
        me = User.query.get(uid)
        projects = []
        if me.role in ['external', 'admin']:
            # External/Admin see all projects
            projects = Project.query.order_by(Project.created_at.desc()).all()
        elif me.role == 'student':
            # Projects linked to workspaces where the student is a member
            ws_ids = [m.workspace_id for m in Membership.query.filter_by(user_id=uid).all()]
            if ws_ids:
                projects = Project.query.filter(Project.workspace_id.in_(ws_ids)).order_by(Project.created_at.desc()).all()
        def ser(p):
            return {
                'id': p.id,
                'title': p.title,
                'description': p.description,
                'created_by': p.created_by,
                'workspace_id': p.workspace_id,
                'status': p.status,
                'created_at': p.created_at.isoformat()
            }
        return jsonify([ser(p) for p in projects]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/api/projects/<int:project_id>/submit', methods=['POST'])
@jwt_required()
def submit_project(project_id):
    try:
        uid = get_jwt_identity()
        me = User.query.get(uid)
        if me.role != 'student':
            return jsonify({'error': 'Only students can submit'}), 403
        data = request.get_json()
        sub = ProjectSubmission(project_id=project_id, student_id=uid, content_url=data.get('content_url'), notes=data.get('notes',''))
        db.session.add(sub)
        # Update project status
        proj = Project.query.get(project_id)
        if proj: proj.status = 'submitted'
        db.session.commit()
        return jsonify({'message': 'Submission recorded', 'submission_id': sub.id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/api/submissions/<int:submission_id>/review', methods=['POST'])
@jwt_required()
def review_submission(submission_id):
    try:
        uid = get_jwt_identity()
        me = User.query.get(uid)
        if me.role not in ['external', 'admin']:
            return jsonify({'error': 'Only external agency or admin can review'}), 403
        data = request.get_json()
        status = data.get('status', 'approved')  # approved | rework | rejected
        if status not in ['approved', 'rework', 'rejected']:
            return jsonify({'error': 'Invalid status'}), 400
        review = ProjectReview(submission_id=submission_id, reviewer_id=uid, status=status, feedback=data.get('feedback',''))
        db.session.add(review)
        # Update project status via submission
        sub = ProjectSubmission.query.get(submission_id)
        if sub:
            proj = Project.query.get(sub.project_id)
            if proj:
                proj.status = 'reviewed' if status == 'approved' else ('rework' if status == 'rework' else 'rejected')
        db.session.commit()
        return jsonify({'message': 'Review saved', 'id': review.id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Student selection and workspace invitation
@api.route('/api/workspaces/<int:workspace_id>/invite-students', methods=['POST'])
@jwt_required()
def invite_students_to_workspace(workspace_id):
    try:
        user_id = get_jwt_identity()
        current_user = User.query.get(user_id)
        
        # Only external agencies and admins can invite students
        if current_user.role not in ['external', 'admin']:
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        data = request.get_json()
        student_ids = data.get('student_ids', [])
        
        if not student_ids:
            return jsonify({'error': 'No students selected'}), 400
        
        # Check if workspace exists and user has access
        workspace = Workspace.query.get(workspace_id)
        if not workspace:
            return jsonify({'error': 'Workspace not found'}), 404
        
        # Check if user is member of workspace
        membership = Membership.query.filter_by(user_id=user_id, workspace_id=workspace_id).first()
        if not membership or membership.role not in ['owner', 'admin']:
            return jsonify({'error': 'Insufficient permissions for this workspace'}), 403
        
        invited_students = []
        for student_id in student_ids:
            # Check if student exists and is actually a student
            student = User.query.get(student_id)
            if not student or student.role != 'student':
                continue
            
            # Check if already invited or member
            existing = Membership.query.filter_by(user_id=student_id, workspace_id=workspace_id).first()
            if existing:
                continue
            
            # Create invitation
            invitation = Membership(
                user_id=student_id,
                workspace_id=workspace_id,
                role='member',
                status='invited',
                invited_by=user_id
            )
            db.session.add(invitation)
            invited_students.append({
                'id': student.id,
                'name': f"{student.first_name} {student.last_name}",
                'email': student.email
            })
        
        db.session.commit()
        
        return jsonify({
            'message': f'Invited {len(invited_students)} students',
            'invited_students': invited_students
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api.route('/api/workspaces/<int:workspace_id>/invitations', methods=['GET'])
@jwt_required()
def get_workspace_invitations(workspace_id):
    try:
        user_id = get_jwt_identity()
        current_user = User.query.get(user_id)
        
        # Check if user is accepted member of workspace
        membership = Membership.query.filter_by(user_id=user_id, workspace_id=workspace_id, status='accepted').first()
        if not membership:
            return jsonify({'error': 'Access denied'}), 403
        
        # Get all invitations for this workspace
        invitations = Membership.query.filter_by(workspace_id=workspace_id, status='invited').all()
        
        invitation_list = []
        for invitation in invitations:
            student = User.query.get(invitation.user_id)
            inviter = User.query.get(invitation.invited_by)
            invitation_list.append({
                'id': invitation.id,
                'student': {
                    'id': student.id,
                    'name': f"{student.first_name} {student.last_name}",
                    'email': student.email
                },
                'invited_by': {
                    'id': inviter.id,
                    'name': f"{inviter.first_name} {inviter.last_name}"
                },
                'invited_at': invitation.invited_at.isoformat()
            })
        
        return jsonify(invitation_list), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Get user's workspace invitations
@api.route('/api/my-invitations', methods=['GET'])
@jwt_required()
def get_my_invitations():
    try:
        user_id = get_jwt_identity()
        
        # Get all invitations for this user
        invitations = Membership.query.filter_by(user_id=user_id, status='invited').all()
        
        invitation_list = []
        for invitation in invitations:
            workspace = Workspace.query.get(invitation.workspace_id)
            inviter = User.query.get(invitation.invited_by)
            invitation_list.append({
                'id': invitation.id,
                'workspace': {
                    'id': workspace.id,
                    'name': workspace.name,
                    'description': workspace.description
                },
                'invited_by': {
                    'id': inviter.id,
                    'name': f"{inviter.first_name} {inviter.last_name}"
                },
                'invited_at': invitation.invited_at.isoformat()
            })
        
        return jsonify(invitation_list), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/api/workspaces/<int:workspace_id>/invitations/<int:invitation_id>/respond', methods=['POST'])
@jwt_required()
def respond_to_workspace_invitation(workspace_id, invitation_id):
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        action = data.get('action')  # 'accept' or 'decline'
        
        if action not in ['accept', 'decline']:
            return jsonify({'error': 'Invalid action'}), 400
        
        # Get invitation
        invitation = Membership.query.get(invitation_id)
        # Only enforce that the invitation belongs to this user; tolerate path workspace_id mismatches
        if not invitation or invitation.user_id != user_id:
            return jsonify({'error': 'Invitation not found'}), 404
        
        if invitation.status != 'invited':
            return jsonify({'error': 'Invitation already responded to'}), 400
        
        if action == 'accept':
            invitation.status = 'accepted'
            invitation.joined_at = datetime.utcnow()
        else:
            invitation.status = 'declined'
        
        db.session.commit()
        
        return jsonify({
            'message': f'Invitation {action}ed successfully',
            'status': invitation.status
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Simpler endpoint: respond to invitation by ID only (no workspace_id path dependency)
@api.route('/api/invitations/<int:invitation_id>/respond', methods=['POST'])
@jwt_required()
def respond_to_invitation_simple(invitation_id):
    try:
        user_id = get_jwt_identity()
        data = request.get_json() or {}
        action = data.get('action')  # 'accept' or 'decline'
        if action not in ['accept', 'decline']:
            return jsonify({'error': 'Invalid action'}), 400
        invitation = Membership.query.get(invitation_id)
        if not invitation or invitation.user_id != int(user_id):
            return jsonify({'error': 'Invitation not found'}), 404
        if invitation.status != 'invited':
            return jsonify({'error': 'Invitation already responded to'}), 400
        if action == 'accept':
            invitation.status = 'accepted'
            invitation.joined_at = datetime.utcnow()
        else:
            invitation.status = 'declined'
        db.session.commit()
        return jsonify({'message': f'Invitation {action}ed successfully', 'status': invitation.status, 'workspace_id': invitation.workspace_id}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Workspace member management
@api.route('/api/workspaces/<int:workspace_id>/members', methods=['GET'])
@jwt_required()
def get_workspace_members(workspace_id):
    try:
        user_id = get_jwt_identity()
        
        # Check if user is accepted member of workspace
        membership = Membership.query.filter_by(user_id=user_id, workspace_id=workspace_id, status='accepted').first()
        if not membership:
            return jsonify({'error': 'Access denied'}), 403
        
        # Get all members
        memberships = Membership.query.filter_by(workspace_id=workspace_id).all()
        
        member_list = []
        for membership in memberships:
            user = User.query.get(membership.user_id)
            member_list.append({
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'role': membership.role,
                'joined_at': membership.joined_at.isoformat()
            })
        
        return jsonify(member_list), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/api/workspaces/<int:workspace_id>/members', methods=['POST'])
@jwt_required()
def add_workspace_member(workspace_id):
    try:
        user_id = get_jwt_identity()
        
        # Check if user is admin or owner
        membership = Membership.query.filter_by(user_id=user_id, workspace_id=workspace_id).first()
        if not membership or membership.role not in ['owner', 'admin']:
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        data = request.get_json()
        member_email = data['email']
        
        # Find user by email
        member = User.query.filter_by(email=member_email).first()
        if not member:
            return jsonify({'error': 'User not found'}), 404
        
        # Check if already a member
        existing_membership = Membership.query.filter_by(user_id=member.id, workspace_id=workspace_id).first()
        if existing_membership:
            return jsonify({'error': 'User is already a member'}), 400
        
        # Add member
        new_membership = Membership(
            user_id=member.id,
            workspace_id=workspace_id,
            role=data.get('role', 'member')
        )
        
        db.session.add(new_membership)
        db.session.commit()
        
        return jsonify({
            'message': 'Member added successfully',
            'member': {
                'id': member.id,
                'username': member.username,
                'first_name': member.first_name,
                'last_name': member.last_name,
                'role': new_membership.role
            }
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
