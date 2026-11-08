import { ValidationResult } from "../utils/ValidationUtils";

export interface EmailValidatorOptions {
  domainWhitelist?: string[];
}

export function validateEmail(email: string, options: EmailValidatorOptions = {}): ValidationResult {
  const domainWhitelist = options.domainWhitelist || [];

  const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+$/;
  const domainRegex = /^[a-zA-Z0-9.-]+$/;

  if (!emailRegex.test(email)) {
    return { valid: false, message: "Invalid email format" };
  }

  const [localPart, domainPart] = email.split("@");

  if (!domainRegex.test(domainPart)) {
    return { valid: false, message: "Invalid domain format" };
  }

  if (!domainWhitelist.includes(domainPart)) {
    return { valid: false, message: "Domain not allowed" };
  }

  return { valid: true, message: "Email is valid" };
}
