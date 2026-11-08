import { ValidationResult } from "../utils/ValidationUtils";

export interface PhoneNumberValidatorOptions {
  countryCodes?: string[];
}

export function validatePhoneNumber(phoneNumber: string, options: PhoneNumberValidatorOptions = {}): ValidationResult {
  const countryCodes = options.countryCodes || [];

  const phoneNumberRegex = /^[+]?[0-9]{1,15}$/;

  if (!phoneNumberRegex.test(phoneNumber)) {
    return { valid: false, message: 'Invalid phone number format' };
  }

  if (!countryCodes.includes(phoneNumber[0])) {
    return { valid: false, message: 'Invalid country code' };
  }

  return { valid: true, message: 'Phone number is valid' };
}
