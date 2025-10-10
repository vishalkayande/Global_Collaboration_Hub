# API Documentation

This document describes the REST API endpoints for the Global Collaboration Hub.

## Base URL

```
http://localhost:5000/api
```

## Authentication

Most endpoints require authentication using JWT tokens. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## Endpoints

### Authentication

#### POST /signup
Create a new user account.

**Request Body:**
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "password": "securepassword"
}
```

**Response:**
```json
{
  "message": "User created successfully",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

#### POST /login
Authenticate user and get access token.

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "securepassword"
}
```

**Response:**
```json
{
  "message": "Login successful",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

#### POST /logout
Logout user (invalidate token).

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "message": "Logout successful"
}
```

### User Profile

#### GET /profile
Get current user's profile information.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "profile_picture": null,
  "bio": null,
  "created_at": "2024-01-01T00:00:00"
}
```

#### PUT /profile
Update current user's profile.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "bio": "Software Developer"
}
```

**Response:**
```json
{
  "message": "Profile updated successfully"
}
```

### Workspaces

#### GET /workspaces
Get all workspaces for the current user.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
[
  {
    "id": 1,
    "name": "Project Alpha",
    "description": "Main project workspace",
    "role": "owner",
    "created_at": "2024-01-01T00:00:00"
  }
]
```

#### POST /workspaces
Create a new workspace.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "name": "Project Alpha",
  "description": "Main project workspace"
}
```

**Response:**
```json
{
  "message": "Workspace created successfully",
  "workspace": {
    "id": 1,
    "name": "Project Alpha",
    "description": "Main project workspace",
    "role": "owner"
  }
}
```

#### GET /workspaces/{workspace_id}/members
Get all members of a workspace.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
[
  {
    "id": 1,
    "username": "johndoe",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "role": "owner",
    "joined_at": "2024-01-01T00:00:00"
  }
]
```

#### POST /workspaces/{workspace_id}/members
Add a member to a workspace.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "email": "jane@example.com",
  "role": "member"
}
```

**Response:**
```json
{
  "message": "Member added successfully",
  "member": {
    "id": 2,
    "username": "janesmith",
    "first_name": "Jane",
    "last_name": "Smith",
    "role": "member"
  }
}
```

### Messages

#### GET /workspaces/{workspace_id}/messages
Get messages for a workspace.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
[
  {
    "id": 1,
    "content": "Hello team!",
    "message_type": "text",
    "file_path": null,
    "user": {
      "id": 1,
      "username": "johndoe",
      "first_name": "John",
      "last_name": "Doe"
    },
    "created_at": "2024-01-01T00:00:00"
  }
]
```

### Files

#### GET /workspaces/{workspace_id}/files
Get all files in a workspace.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
[
  {
    "id": 1,
    "filename": "document.pdf",
    "original_filename": "project_document.pdf",
    "file_size": 1024000,
    "file_type": "application/pdf",
    "description": "Project requirements document",
    "uploaded_by": {
      "id": 1,
      "username": "johndoe",
      "first_name": "John",
      "last_name": "Doe"
    },
    "created_at": "2024-01-01T00:00:00"
  }
]
```

#### POST /workspaces/{workspace_id}/files
Upload a file to a workspace.

**Headers:** `Authorization: Bearer <token>`

**Request Body:** `multipart/form-data`
- `file`: The file to upload
- `description`: Optional file description

**Response:**
```json
{
  "message": "File uploaded successfully",
  "file": {
    "id": 1,
    "filename": "document.pdf",
    "original_filename": "project_document.pdf",
    "file_size": 1024000,
    "file_type": "application/pdf"
  }
}
```

#### GET /files/{file_id}/download
Download a file.

**Headers:** `Authorization: Bearer <token>`

**Response:** File content with appropriate headers for download.

### Tasks

#### GET /workspaces/{workspace_id}/tasks
Get all tasks in a workspace.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
[
  {
    "id": 1,
    "title": "Complete user authentication",
    "description": "Implement login and signup functionality",
    "status": "in_progress",
    "priority": "high",
    "due_date": "2024-01-15T00:00:00",
    "created_by": {
      "id": 1,
      "username": "johndoe",
      "first_name": "John",
      "last_name": "Doe"
    },
    "assigned_to": {
      "id": 2,
      "username": "janesmith",
      "first_name": "Jane",
      "last_name": "Smith"
    },
    "created_at": "2024-01-01T00:00:00"
  }
]
```

#### POST /workspaces/{workspace_id}/tasks
Create a new task.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "title": "Complete user authentication",
  "description": "Implement login and signup functionality",
  "priority": "high",
  "assigned_to": 2,
  "due_date": "2024-01-15T00:00:00"
}
```

**Response:**
```json
{
  "message": "Task created successfully",
  "task": {
    "id": 1,
    "title": "Complete user authentication",
    "description": "Implement login and signup functionality",
    "status": "pending",
    "priority": "high",
    "due_date": "2024-01-15T00:00:00"
  }
}
```

#### PUT /tasks/{task_id}
Update a task.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "title": "Updated task title",
  "description": "Updated description",
  "status": "completed",
  "priority": "medium",
  "assigned_to": 2,
  "due_date": "2024-01-20T00:00:00"
}
```

**Response:**
```json
{
  "message": "Task updated successfully"
}
```

#### DELETE /tasks/{task_id}
Delete a task.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "message": "Task deleted successfully"
}
```

## WebSocket Events

The application uses Socket.IO for real-time communication.

### Connection

Connect to: `http://localhost:5000`

### Events

#### join_workspace
Join a workspace room for real-time updates.

**Emit:**
```json
{
  "workspace_id": 1
}
```

#### leave_workspace
Leave a workspace room.

**Emit:**
```json
{
  "workspace_id": 1
}
```

#### send_message
Send a message to a workspace.

**Emit:**
```json
{
  "workspace_id": 1,
  "content": "Hello team!"
}
```

#### new_message
Receive new messages in real-time.

**Listen:**
```json
{
  "id": 1,
  "content": "Hello team!",
  "user": {
    "id": 1,
    "username": "johndoe",
    "first_name": "John",
    "last_name": "Doe"
  },
  "created_at": "2024-01-01T00:00:00"
}
```

## Error Responses

All endpoints may return error responses in the following format:

```json
{
  "error": "Error message describing what went wrong"
}
```

### Common HTTP Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error

## Rate Limiting

Currently, there are no rate limits implemented. In production, consider implementing rate limiting to prevent abuse.

## CORS

The API supports CORS for cross-origin requests. The allowed origins are configured in the Flask application.

## File Upload Limits

- Maximum file size: 16MB
- Allowed file types: txt, pdf, png, jpg, jpeg, gif, doc, docx, xls, xlsx, ppt, pptx

## Database Schema

The API uses the following main entities:

- **Users**: User accounts and profiles
- **Workspaces**: Project workspaces
- **Memberships**: User-workspace relationships
- **Messages**: Chat messages
- **Files**: Uploaded files
- **Tasks**: Task management

For detailed schema information, see `database/schema.sql`.
