import { ValidationResult } from "../utils/ValidationUtils";

export interface PasswordValidatorOptions {
  minLength?: number;
  hasUpperCase?: boolean;
  hasLowerCase?: boolean;
  hasNumber?: boolean;
  hasSpecialChar?: boolean;
}

export function validatePassword(password: string, options: PasswordValidatorOptions = {}): ValidationResult {
  const minLength = options.minLength || 8;
  const hasUpperCase = options.hasUpperCase || true;
  const hasLowerCase = options.hasLowerCase || true;
  const hasNumber = options.hasNumber || true;
  const hasSpecialChar = options.hasSpecialChar || true;

  if (password.length < minLength) {
    return { valid: false, message: `Password must be at least ${minLength} characters long` };
  }

  const hasUpperCaseRegex = /[A-Z]/;
  const hasLowerCaseRegex = /[a-z]/;
  const hasNumberRegex = /[0-9]/;
  const hasSpecialCharRegex = /[!@#$%^&*(),.?":{}|<>]/;

  if (!hasUpperCase && !hasLowerCase && !hasNumber && !hasSpecialChar) {
    return {
      valid: false,
      message: "Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character"
    };
  }

  if (!hasUpperCaseRegex.test(password) && hasUpperCase) {
    return { valid: false, message: "Password must contain at least one uppercase letter" };
  }

  if (!hasLowerCaseRegex.test(password) && hasLowerCase) {
    return { valid: false, message: "Password must contain at least one lowercase letter" };
  }

  if (!hasNumberRegex.test(password) && hasNumber) {
    return { valid: false, message: "Password must contain at least one number" };
  }

  if (!hasSpecialCharRegex.test(password) && hasSpecialChar) {
    return { valid: false, message: "Password must contain at least one special character" };
  }

  return { valid: true, message: "Password is valid" };
}
