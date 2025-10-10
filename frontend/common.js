// Shared utilities for Global Collaboration Hub pages

const API_BASE_URL = 'http://localhost:5000/api';

function getToken() {
    return localStorage.getItem('token');
}

function setToken(token) {
    localStorage.setItem('token', token);
}

function clearAuth() {
    localStorage.removeItem('token');
    localStorage.removeItem('currentUser');
}

function saveCurrentUser(user) {
    localStorage.setItem('currentUser', JSON.stringify(user));
}

function getCurrentUser() {
    try {
        return JSON.parse(localStorage.getItem('currentUser'));
    } catch (_) {
        return null;
    }
}

function requireAuth(redirectTo = 'login.html') {
    const token = getToken();
    if (!token) {
        window.location.href = redirectTo;
        return null;
    }
    return token;
}

function go(path) {
    window.location.href = path;
}

function qs(id) {
    return document.getElementById(id);
}

function notify(message, type = 'info') {
    const div = document.createElement('div');
    div.className = `notification status-${type}`;
    div.textContent = message;
    div.style.cssText = `position: fixed; top: 20px; right: 20px; padding: 1rem 1.5rem; border-radius: 6px; color: white; font-weight: 500; z-index: 10000;`;
    div.style.backgroundColor = type === 'success' ? '#4caf50' : type === 'error' ? '#f44336' : '#2196f3';
    document.body.appendChild(div);
    setTimeout(() => div.remove(), 2500);
}





