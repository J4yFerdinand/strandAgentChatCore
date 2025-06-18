# manage_user_requests.py

import os
import json
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, EmailStr, validator
from strands import tool

class User(BaseModel):
    documentNumber: int
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    manual_review_required: Optional[bool] = False
    
    @validator('phone')
    def validate_phone(cls, v):
        if v is not None and not v.startswith('+'):
            raise ValueError('Phone number must include country code starting with +')
        return v

def _ensure_users_directory():
    """Ensure the users directory exists"""
    os.makedirs("users", exist_ok=True)

def _get_user_file_path(document_number: int) -> str:
    """Get the file path for a user's JSON file"""
    return f"users/{document_number}.json"

@tool
def create_user(document_number: int, first_name: Optional[str] = None, last_name: Optional[str] = None, phone: Optional[str] = None, email: Optional[str] = None, manual_review_required: bool = False) -> str:
    """Create a new user record
    
    Args:
        document_number: User's document/ID number (must be unique)
        first_name: User's first name (optional)
        last_name: User's last name (optional)
        phone: User's phone number with country code (e.g., +573123456789) (optional)
        email: User's email address (optional)
        manual_review_required: Whether manual review is required for this user (default: False)
    """
    try:
        _ensure_users_directory()
        
        # Check if user already exists
        file_path = _get_user_file_path(document_number)
        if os.path.exists(file_path):
            return f"Error: User with document number {document_number} already exists"
        
        # Validate user data
        user = User(
            documentNumber=document_number,
            firstName=first_name,
            lastName=last_name,
            phone=phone,
            email=email,
            manual_review_required=manual_review_required
        )
        
        # Save user to JSON file
        with open(file_path, 'w') as f:
            json.dump(user.dict(), f, indent=2)
        
        name_display = f"{first_name or ''} {last_name or ''}".strip() or f"Document {document_number}"
        return f"User {name_display} created successfully with document number {document_number}"
        
    except Exception as e:
        return f"Error creating user: {str(e)}"

@tool
def get_user(document_number: int) -> str:
    """Get user information by document number
    
    Args:
        document_number: User's document/ID number
    """
    try:
        file_path = _get_user_file_path(document_number)
        
        if not os.path.exists(file_path):
            return f"Error: User with document number {document_number} not found"
        
        with open(file_path, 'r') as f:
            user_data = json.load(f)
        
        name = f"{user_data.get('firstName', 'N/A')} {user_data.get('lastName', 'N/A')}".strip()
        if name == "N/A N/A":
            name = "N/A"
        
        phone = user_data.get('phone', 'N/A')
        email = user_data.get('email', 'N/A')
        review_status = "Yes" if user_data.get('manual_review_required', False) else "No"
        
        return f"User found: {name}, Phone: {phone}, Email: {email}, Manual Review Required: {review_status}"
        
    except Exception as e:
        return f"Error retrieving user: {str(e)}"

@tool
def update_user(document_number: int, first_name: Optional[str] = None, last_name: Optional[str] = None, phone: Optional[str] = None, email: Optional[str] = None, manual_review_required: Optional[bool] = None) -> str:
    """Update user information
    
    Args:
        document_number: User's document/ID number
        first_name: New first name (optional)
        last_name: New last name (optional)
        phone: New phone number with country code (optional)
        email: New email address (optional)
        manual_review_required: Whether manual review is required for this user (optional)
    """
    try:
        file_path = _get_user_file_path(document_number)
        
        if not os.path.exists(file_path):
            return f"Error: User with document number {document_number} not found"
        
        # Load existing user data
        with open(file_path, 'r') as f:
            user_data = json.load(f)
        
        # Update fields if provided
        if first_name is not None:
            user_data['firstName'] = first_name
        if last_name is not None:
            user_data['lastName'] = last_name
        if phone is not None:
            user_data['phone'] = phone
        if email is not None:
            user_data['email'] = email
        if manual_review_required is not None:
            user_data['manual_review_required'] = manual_review_required
        
        # Validate updated data
        user = User(**user_data)
        
        # Save updated data
        with open(file_path, 'w') as f:
            json.dump(user.dict(), f, indent=2)
        
        return f"User {user_data['firstName']} {user_data['lastName']} updated successfully"
        
    except Exception as e:
        return f"Error updating user: {str(e)}"

@tool
def delete_user(document_number: int) -> str:
    """Delete a user record
    
    Args:
        document_number: User's document/ID number
    """
    try:
        file_path = _get_user_file_path(document_number)
        
        if not os.path.exists(file_path):
            return f"Error: User with document number {document_number} not found"
        
        # Get user info before deletion
        with open(file_path, 'r') as f:
            user_data = json.load(f)
        
        # Delete the file
        os.remove(file_path)
        
        return f"User {user_data['firstName']} {user_data['lastName']} with document number {document_number} deleted successfully"
        
    except Exception as e:
        return f"Error deleting user: {str(e)}"

@tool
def list_all_users() -> str:
    """List all users in the system
    """
    try:
        _ensure_users_directory()
        
        user_files = [f for f in os.listdir("users") if f.endswith('.json')]
        
        if not user_files:
            return "No users found in the system"
        
        users_info = []
        for file_name in user_files:
            with open(f"users/{file_name}", 'r') as f:
                user_data = json.load(f)
                
                name = f"{user_data.get('firstName', 'N/A')} {user_data.get('lastName', 'N/A')}".strip()
                if name == "N/A N/A":
                    name = "N/A"
                
                phone = user_data.get('phone', 'N/A')
                email = user_data.get('email', 'N/A')
                review_status = "Yes" if user_data.get('manual_review_required', False) else "No"
                
                users_info.append(f"Doc: {user_data['documentNumber']}, Name: {name}, Phone: {phone}, Email: {email}, Manual Review: {review_status}")
        
        return "Users in system:\n" + "\n".join(users_info)
        
    except Exception as e:
        return f"Error listing users: {str(e)}"