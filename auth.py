"""
Authentication module for the construction material recommendation system.
This module handles user authentication and session management.
"""

import streamlit as st
import re
from db_utils import authenticate_user, register_user


# to check the valid state of a mail
def is_valid_email(email):
    """
    Check if an email is valid.

    Args:
        email (str): Email address

    Returns:
        bool: True if email is valid, False otherwise
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def is_valid_username(username):
    """
    Check if a username is valid.

    Args:
        username (str): Username

    Returns:
        bool: True if username is valid, False otherwise
    """
    # Username must be 3-20 characters and can only contain alphanumeric characters and underscores
    pattern = r"^[a-zA-Z0-9_]{3,20}$"
    return re.match(pattern, username) is not None


def is_valid_password(password):
    """
    Check if a password is valid.

    Args:
        password (str): Password

    Returns:
        bool: True if password is valid, False otherwise
    """
    # Password must be at least 8 characters and contain at least one uppercase letter,
    # one lowercase letter, one number, and one special character
    return len(password) >= 8


def init_session_state():
    """Initialize session state variables for authentication."""
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if "user_id" not in st.session_state:
        st.session_state.user_id = None

    if "username" not in st.session_state:
        st.session_state.username = None


def login_user(username_or_email, password):
    """
    Log in a user.

    Args:
        username_or_email (str): Username or email
        password (str): Password

    Returns:
        tuple: (success, message)
    """
    if not username_or_email or not password:
        return False, "Please enter both username/email and password."

    user = authenticate_user(username_or_email, password)

    if user:
        st.session_state.logged_in = True
        st.session_state.user_id = user.id
        st.session_state.username = user.username
        return True, f"Welcome back, {user.username}!"
    else:
        return False, "Invalid username/email or password."


def register_new_user(username, email, password, confirm_password):
    """
    Register a new user.

    Args:
        username (str): Username
        email (str): Email address
        password (str): Password
        confirm_password (str): Confirm password

    Returns:
        tuple: (success, message)
    """
    # Validate input
    if not username or not email or not password or not confirm_password:
        return False, "Please fill in all fields."

    if not is_valid_username(username):
        return (
            False,
            "Username must be 3-20 characters and can only contain letters, numbers, and underscores.",
        )

    if not is_valid_email(email):
        return False, "Please enter a valid email address."

    if not is_valid_password(password):
        return False, "Password must be at least 8 characters long."

    if password != confirm_password:
        return False, "Passwords do not match."

    # Register user
    success = register_user(username, email, password)

    if success:
        return True, "Registration successful! Please log in."
    else:
        return False, "Username or email already exists."


def logout_user():
    """Log out the current user."""
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = None


def display_login_page():
    """
    Display the login page.

    Returns:
        bool: True if user is logged in, False otherwise
    """
    init_session_state()

    if st.session_state.logged_in:
        return True

    login_tab, register_tab = st.tabs(["Login", "Register"])

    with login_tab:
        st.subheader("Login")
        username_or_email = st.text_input("Username or Email", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login", type="primary", key="login_button"):
            success, message = login_user(username_or_email, password)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)

    with register_tab:
        st.subheader("Register")
        username = st.text_input("Username", key="register_username")
        email = st.text_input("Email", key="register_email")
        password = st.text_input("Password", type="password", key="register_password")
        confirm_password = st.text_input(
            "Confirm Password", type="password", key="register_confirm_password"
        )

        if st.button("Register", type="primary", key="register_button"):
            success, message = register_new_user(
                username, email, password, confirm_password
            )
            if success:
                st.success(message)
            else:
                st.error(message)

    return False
