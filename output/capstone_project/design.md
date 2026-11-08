# Design

## Architecture

To build a comprehensive TypeScript utility that validates email addresses, strong passwords, and phone numbers, we will follow a modular and scalable architecture. This approach will ensure that the utility is easy to maintain and extend.

### Module Structure

1. **src/validators/EmailValidator.ts**: Contains the logic for validating email addresses.
2. **src/validators/PasswordValidator.ts**: Contains the logic for validating strong passwords.
3. **src/validators/PhoneNumberValidator.ts**: Contains the logic for validating phone numbers.
4. **src/utils/ValidationUtils.ts**: Contains utility functions for error handling and validation rules.
5. **src/index.ts**: Entry point for the utility.

### Key TypeScript Types/Interfaces

1. **EmailValidatorOptions**: Interface for configuring email validation rules.
2. **PasswordValidatorOptions**: Interface for configuring password validation rules.
3. **PhoneNumberValidatorOptions**: Interface for configuring phone number validation rules.
4. **ValidationResult**: Interface for the result of a validation operation.

### File Structure (keep it to 1-2 files inside src/)

```
src/
├── validators/
│   ├── EmailValidator.ts
│   ├── PasswordValidator.ts
│   └── PhoneNumberValidator.ts
├── utils/
│   └── ValidationUtils.ts
└── index.ts
```

### Edge Cases

1. **Email Validation**:
   - **Invalid Characters**: Ensure that the email address does not contain invalid characters (e.g., spaces, special characters).
   - **Domain Validation**: Check if the domain part of the email address is valid (e.g., using a regular expression to match valid domain names).
   - **Empty String**: Handle cases where the input string is empty.
   - **Multiple At Symbols**: Ensure that there is only one "@" symbol in the email address.
   - **Missing "@" Symbol**: Handle cases where the "@" symbol is missing.

2. **Password Validation**:
   - **Minimum Length**: Ensure the password meets a minimum length requirement.
   - **Character Requirements**: Check for the presence of at least one uppercase letter, one lowercase letter, one digit, and one special character.
   - **Empty String**: Handle cases where the input string is empty.
   - **Repeating Characters**: Ensure that there are no repeating characters in the password.
   - **Special Characters**: Ensure that the password contains at least one special character.

3. **Phone Number Validation**:
   - **Format Validation**: Check if the phone number is in a valid format (e.g., using a regular expression to match common formats).
   - **Empty String**: Handle cases where the input string is empty.
   - **Invalid Characters**: Ensure that the phone number does not contain invalid characters (e.g., letters).
   - **Missing Country Code**: Handle cases where the country code is missing.

4. **Error Handling**:
   - **Detailed Error Messages**: Provide clear and informative error messages to help users understand what went wrong.
   - **Consistent Error Handling**: Ensure that all error messages are consistent and follow a standardized format.
   - **User-Friendly Messages**: Provide user-friendly error messages that are easy to understand and follow a consistent tone.

By following these guidelines and patterns, you can build a robust and maintainable TypeScript utility for validating email addresses, strong passwords, and phone numbers.