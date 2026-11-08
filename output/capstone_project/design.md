# Design

## Architecture
The utility is designed with a modular approach, separating concerns for email, password, and phone number validation. Each validation function is implemented as a pure function, ensuring predictability and ease of testing. Regular expressions are utilized for efficient pattern matching, and TypeScript's type system is leveraged for type safety. Error handling is incorporated to provide meaningful feedback when validation fails.

## Key TypeScript Types/Interfaces
```typescript
type Email = string;
type Password = string;
type PhoneNumber = string;

enum ValidationError {
    InvalidEmail = "Invalid email format",
    WeakPassword = "Password must be at least 8 characters long and contain a mix of letters, numbers, and symbols.",
    InvalidPhoneNumber = "Invalid phone number format"
}

interface ValidationResult {
    isValid: boolean;
    error?: ValidationError;
}
```

## File Structure
```
src/
├── validation.ts
```

### validation.ts
```typescript
type Email = string;
type Password = string;
type PhoneNumber = string;

enum ValidationError {
    InvalidEmail = "Invalid email format",
    WeakPassword = "Password must be at least 8 characters long and contain a mix of letters, numbers, and symbols.",
    InvalidPhoneNumber = "Invalid phone number format"
}

interface ValidationResult {
    isValid: boolean;
    error?: ValidationError;
}

function validateEmail(email: Email): ValidationResult {
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    if (emailRegex.test(email)) {
        return { isValid: true };
    }
    return { isValid: false, error: ValidationError.InvalidEmail };
}

function validatePassword(password: Password): ValidationResult {
    const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
    if (passwordRegex.test(password)) {
        return { isValid: true };
    }
    return { isValid: false, error: ValidationError.WeakPassword };
}

function validatePhoneNumber(phone: PhoneNumber): ValidationResult {
    const phoneRegex = /^\+?[1-9]\d{1,14}$/; // E.164 format
    if (phoneRegex.test(phone)) {
        return { isValid: true };
    }
    return { isValid: false, error: ValidationError.InvalidPhoneNumber };
}

// Example usage
console.log(validateEmail("test@example.com")); // { isValid: true }
console.log(validatePassword("StrongP@ssw0rd")); // { isValid: true }
console.log(validatePhoneNumber("+1234567890")); // { isValid: true }
```

## Edge Cases
- **Email Validation Edge Cases**:
  - International characters and special characters in local parts.
  - Maximum length of 254 characters.
  
- **Password Validation Edge Cases**:
  - Minimum length of 8 characters.
  - At least one uppercase letter, one lowercase letter, one number, and one special character.
  - Check against common passwords to prevent weak choices.

- **Phone Number Validation Edge Cases**:
  - Support for international formats (E.164).
  - Handle various lengths and formats while ensuring validity.

- **Input Sanitization**: Always sanitize inputs to prevent injection attacks or unexpected behavior.

- **Performance Considerations**: Optimize regex operations for large-scale applications to ensure efficient validation.