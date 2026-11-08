export interface ValidationResult {
  valid: boolean;
  message: string;
}

export function generateErrorMessage(error: string): string {
  return `Validation error: ${error}`;
}

export function handleValidationResult(result: ValidationResult): void {
  if (!result.valid) {
    console.error(generateErrorMessage(result.message));
  }
}
