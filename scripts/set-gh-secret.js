// DEPRECATED: This helper was used to programmatically set repository secrets during setup.
// It has been intentionally removed from active use. If you still need to set secrets programmatically,
// prefer using the official GitHub CLI (`gh secret set`) or the GitHub Actions secrets REST API with
// appropriate safeguards. See docs/RECYCLING-AI.md for recommended workflows and the `.github/workflows`
// test that validates `OPENAI_API_KEY` is present and usable.

console.log('scripts/set-gh-secret.js is deprecated and intentionally disabled.');
