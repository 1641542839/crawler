# Crawler - User Registration Application

A simple web application with a user registration form that includes validation and data persistence.

## Features

- Clean and modern user interface
- Client-side form validation
- Real-time validation feedback
- Responsive design for mobile and desktop
- Data persistence using localStorage
- Password strength requirements

## Registration Form Fields

- **Username** (required): 3-20 characters, alphanumeric and underscores only
- **Email** (required): Valid email format
- **Password** (required): Minimum 8 characters, must include:
  - At least one uppercase letter
  - At least one lowercase letter
  - At least one number
- **Confirm Password** (required): Must match password
- **Full Name** (optional): User's full name

## How to Use

1. Open `index.html` in a web browser
2. Fill in the registration form
3. Submit the form to create a new user account
4. User data is stored in the browser's localStorage

## File Structure

```
crawler/
├── index.html      # Main HTML file with registration form
├── styles.css      # Styling for the registration form
├── script.js       # Form validation and submission logic
└── README.md       # This file
```

## Data Storage

User registration data is stored in the browser's localStorage for demonstration purposes. In a production environment, this should be replaced with a proper backend API and database.

## Validation Rules

- Username: Must be 3-20 characters, alphanumeric with underscores
- Email: Must be a valid email address format
- Password: Must be at least 8 characters with uppercase, lowercase, and numbers
- Confirm Password: Must match the password field

## Browser Compatibility

This application works in all modern browsers that support:
- HTML5
- CSS3
- ES6 JavaScript
- localStorage API
