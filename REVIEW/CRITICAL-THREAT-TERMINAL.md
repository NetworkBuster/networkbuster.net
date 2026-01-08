# Review: Critical Threat Terminal — Kit Checksum & Labeling

This PR stages artifacts and metadata for review related to labeling and tagging drone kits with SHA-256 checksums.

Summary of staged items:

- `test-standstill-v1.0.0.zip` and `test-standstill-v1.0.0.zip.sha256` (checksum file present)
- `releases/test-standstill-v1.0.0/` (packaged artifacts)
- Release notes updated in `RELEASES.md`
- Packaging scripts in `scripts/` (`make_standstill_release.*`, `package_standstill_only.*`)

Reviewer checklist:

- [ ] Verify checksum files exist for all kit artifacts
- [ ] Confirm `.sha256` contents and expected format (`<SHA256>  <filename>`)
- [ ] Confirm `RELEASES.md` has updated checksum and release notes
- [ ] Approve tag names and tagging policy (e.g., `kit-<name>-sha256-<short>`)
- [ ] Review label/print assets (PDF/PNG) when generated
- [ ] Approve pushing tags and uploading checksum assets to GitHub Releases

Notes & next steps:
- I will compute checksums for additional kit files (if you specify kit locations) and add `.sha256` files.
- After review approval I will create annotated tags `kit-<name>-sha256-<short>` and upload checksums to releases.
- If you want printable labels, I will generate a PDF with QR codes linking to the release asset or checksum file.

If this matches your intent, review the items above and respond with approvals or corrections.
