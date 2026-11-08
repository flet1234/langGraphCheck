// src/types.ts

export type Email = string;
export type Password = string;
export type PhoneNumber = string;

export enum ValidationError {
    None = 'None',
    InvalidEmail = 'Invalid Email',
    WeakPassword = 'Weak Password',
    InvalidPhoneNumber = 'Invalid Phone Number'
}

export interface ValidationResult {
    isValid: boolean;
    error: ValidationError;
}