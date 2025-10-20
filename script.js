document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('registrationForm');
    const successMessage = document.getElementById('success-message');

    // Form field elements
    const username = document.getElementById('username');
    const email = document.getElementById('email');
    const password = document.getElementById('password');
    const confirmPassword = document.getElementById('confirmPassword');

    // Error message elements
    const usernameError = document.getElementById('username-error');
    const emailError = document.getElementById('email-error');
    const passwordError = document.getElementById('password-error');
    const confirmPasswordError = document.getElementById('confirmPassword-error');

    // Validation functions
    function validateUsername() {
        const value = username.value.trim();
        if (value === '') {
            usernameError.textContent = 'Username is required';
            username.classList.add('invalid');
            return false;
        }
        if (value.length < 3) {
            usernameError.textContent = 'Username must be at least 3 characters';
            username.classList.add('invalid');
            return false;
        }
        if (value.length > 20) {
            usernameError.textContent = 'Username must not exceed 20 characters';
            username.classList.add('invalid');
            return false;
        }
        if (!/^[a-zA-Z0-9_]+$/.test(value)) {
            usernameError.textContent = 'Username can only contain letters, numbers, and underscores';
            username.classList.add('invalid');
            return false;
        }
        usernameError.textContent = '';
        username.classList.remove('invalid');
        return true;
    }

    function validateEmail() {
        const value = email.value.trim();
        if (value === '') {
            emailError.textContent = 'Email is required';
            email.classList.add('invalid');
            return false;
        }
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            emailError.textContent = 'Please enter a valid email address';
            email.classList.add('invalid');
            return false;
        }
        emailError.textContent = '';
        email.classList.remove('invalid');
        return true;
    }

    function validatePassword() {
        const value = password.value;
        if (value === '') {
            passwordError.textContent = 'Password is required';
            password.classList.add('invalid');
            return false;
        }
        if (value.length < 8) {
            passwordError.textContent = 'Password must be at least 8 characters';
            password.classList.add('invalid');
            return false;
        }
        if (!/[A-Z]/.test(value)) {
            passwordError.textContent = 'Password must contain at least one uppercase letter';
            password.classList.add('invalid');
            return false;
        }
        if (!/[a-z]/.test(value)) {
            passwordError.textContent = 'Password must contain at least one lowercase letter';
            password.classList.add('invalid');
            return false;
        }
        if (!/[0-9]/.test(value)) {
            passwordError.textContent = 'Password must contain at least one number';
            password.classList.add('invalid');
            return false;
        }
        passwordError.textContent = '';
        password.classList.remove('invalid');
        return true;
    }

    function validateConfirmPassword() {
        const value = confirmPassword.value;
        if (value === '') {
            confirmPasswordError.textContent = 'Please confirm your password';
            confirmPassword.classList.add('invalid');
            return false;
        }
        if (value !== password.value) {
            confirmPasswordError.textContent = 'Passwords do not match';
            confirmPassword.classList.add('invalid');
            return false;
        }
        confirmPasswordError.textContent = '';
        confirmPassword.classList.remove('invalid');
        return true;
    }

    // Add blur event listeners for real-time validation
    username.addEventListener('blur', validateUsername);
    email.addEventListener('blur', validateEmail);
    password.addEventListener('blur', validatePassword);
    confirmPassword.addEventListener('blur', validateConfirmPassword);

    // Also validate confirm password when password changes
    password.addEventListener('input', function() {
        if (confirmPassword.value !== '') {
            validateConfirmPassword();
        }
    });

    // Form submission handler
    form.addEventListener('submit', function(e) {
        e.preventDefault();

        // Validate all fields
        const isUsernameValid = validateUsername();
        const isEmailValid = validateEmail();
        const isPasswordValid = validatePassword();
        const isConfirmPasswordValid = validateConfirmPassword();

        // Check if all validations passed
        if (isUsernameValid && isEmailValid && isPasswordValid && isConfirmPasswordValid) {
            // Prepare user data
            const userData = {
                username: username.value.trim(),
                email: email.value.trim(),
                fullName: document.getElementById('fullName').value.trim(),
                timestamp: new Date().toISOString()
            };

            // Save to localStorage (simulating backend storage)
            const users = JSON.parse(localStorage.getItem('registeredUsers') || '[]');
            users.push(userData);
            localStorage.setItem('registeredUsers', JSON.stringify(users));

            // Show success message
            form.style.display = 'none';
            successMessage.style.display = 'block';

            // Reset form after 3 seconds and show it again
            setTimeout(function() {
                form.reset();
                form.style.display = 'flex';
                successMessage.style.display = 'none';
            }, 3000);
        }
    });
});
