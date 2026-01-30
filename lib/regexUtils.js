/**
 * NetworkBuster - Regex Utility Module
 * Safe regex operations and pattern helpers
 */

/**
 * Escapes special regex characters in a string to use it as a literal pattern
 * Prevents regex injection when using user input in regular expressions
 * 
 * @param {string} str - The string to escape
 * @returns {string} - Escaped string safe for regex use
 * 
 * @example
 * const userInput = "user@email.com";
 * const safe = escapeRegex(userInput);
 * const regex = new RegExp(safe); // Safe: matches literal "user@email.com"
 */
export function escapeRegex(str) {
  if (typeof str !== 'string') {
    throw new TypeError('escapeRegex expects a string argument');
  }
  return str.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

/**
 * Creates a safe RegExp from user input with optional flags
 * 
 * @param {string} pattern - The pattern string (will be escaped)
 * @param {string} flags - Optional regex flags (g, i, m, etc.)
 * @returns {RegExp} - Safe regular expression
 * 
 * @example
 * const regex = createSafeRegex(userInput, 'gi');
 */
export function createSafeRegex(pattern, flags = '') {
  const escaped = escapeRegex(pattern);
  return new RegExp(escaped, flags);
}

/**
 * Tests if a string matches a pattern safely
 * 
 * @param {string} str - String to test
 * @param {string} pattern - Pattern to match (will be escaped)
 * @param {boolean} caseInsensitive - Whether to ignore case
 * @returns {boolean} - True if matches
 * 
 * @example
 * const matches = testPattern("Hello World", "hello", true); // true
 */
export function testPattern(str, pattern, caseInsensitive = false) {
  const flags = caseInsensitive ? 'i' : '';
  const regex = createSafeRegex(pattern, flags);
  return regex.test(str);
}

/**
 * Finds all matches of a pattern in a string (safely escaped)
 * 
 * @param {string} str - String to search
 * @param {string} pattern - Pattern to find (will be escaped)
 * @param {boolean} caseInsensitive - Whether to ignore case
 * @returns {Array<string>} - Array of matches
 * 
 * @example
 * const matches = findMatches("test test TEST", "test", true); // ["test", "test", "TEST"]
 */
export function findMatches(str, pattern, caseInsensitive = false) {
  const flags = 'g' + (caseInsensitive ? 'i' : '');
  const regex = createSafeRegex(pattern, flags);
  return str.match(regex) || [];
}

/**
 * Replaces all occurrences of a pattern safely
 * 
 * @param {string} str - String to modify
 * @param {string} pattern - Pattern to replace (will be escaped)
 * @param {string} replacement - Replacement string
 * @param {boolean} caseInsensitive - Whether to ignore case
 * @returns {string} - Modified string
 * 
 * @example
 * const result = replaceAll("Hello hello HELLO", "hello", "Hi", true); // "Hi Hi Hi"
 */
export function replaceAll(str, pattern, replacement, caseInsensitive = false) {
  const flags = 'g' + (caseInsensitive ? 'i' : '');
  const regex = createSafeRegex(pattern, flags);
  return str.replace(regex, replacement);
}

/**
 * Validates if a string is a valid regex pattern
 * 
 * @param {string} pattern - Pattern to validate
 * @returns {boolean} - True if valid regex
 * 
 * @example
 * const valid = isValidRegex("^[a-z]+$"); // true
 * const invalid = isValidRegex("^[a-z"); // false (unclosed bracket)
 */
export function isValidRegex(pattern) {
  try {
    new RegExp(pattern);
    return true;
  } catch (e) {
    return false;
  }
}

/**
 * Common regex patterns for validation
 */
export const PATTERNS = {
  email: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  url: /^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$/,
  ipv4: /^(\d{1,3}\.){3}\d{1,3}$/,
  ipv6: /^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$/,
  port: /^([1-9][0-9]{0,3}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])$/,
  mac: /^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$/,
  hex: /^#?([0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})$/,
  uuid: /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i,
  phone: /^\+?[\d\s\-\(\)]+$/,
  alphanumeric: /^[a-zA-Z0-9]+$/,
  slug: /^[a-z0-9]+(?:-[a-z0-9]+)*$/
};

/**
 * Validates input against common patterns
 * 
 * @param {string} str - String to validate
 * @param {string} type - Pattern type from PATTERNS
 * @returns {boolean} - True if valid
 * 
 * @example
 * const valid = validate("user@example.com", "email"); // true
 */
export function validate(str, type) {
  const pattern = PATTERNS[type];
  if (!pattern) {
    throw new Error(`Unknown validation type: ${type}`);
  }
  return pattern.test(str);
}

export default {
  escapeRegex,
  createSafeRegex,
  testPattern,
  findMatches,
  replaceAll,
  isValidRegex,
  validate,
  PATTERNS
};
