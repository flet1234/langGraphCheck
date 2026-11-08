// src/validation.ts

import { Email, Password, PhoneNumber, ValidationError, ValidationResult } from './types';

export function validateEmail(email: Email): ValidationResult {
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    if (!emailRegex.test(email)) {
        return { isValid: false, error: ValidationError.InvalidEmail };
    }
    return { isValid: true, error: ValidationError.None };
}

export function validatePassword(password: Password): ValidationResult {
    const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
    if (!passwordRegex.test(password)) {
        return { isValid: false, error: ValidationError.WeakPassword };
    }
    return { isValid: true, error: ValidationError.None };
}

export function validatePhoneNumber(phone: PhoneNumber): ValidationResult {
    const phoneRegex = /^\+?[1-9]\d{1,14}$/;
    if (!phoneRegex.test(phone)) {
        return { isValid: false, error: ValidationError.InvalidPhoneNumber };
    }
    return { isValid: true, error: ValidationError.None };
}