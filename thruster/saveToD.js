// thruster/saveToD backend feature (Raspberry Pi friendly)
// Cross-platform save helper with configurable base directory

const fs = require('fs');
const path = require('path');
const os = require('os');

/**
 * Save content to a specified folder. On Windows this can still target a drive like D:\
 * On Linux (Raspberry Pi), it will use a configurable base directory (env THRUSTER_SAVE_DIR)
 * or default to $HOME/thruster-data.
 *
 * @param {string} folderNameOrPath - The folder name under base dir, or an absolute path
 * @param {string} fileName - The file name to save
 * @param {string|Buffer} content - The content to write
 * @returns {Promise<string>} - Path to the saved file
 */
async function saveToPath(folderNameOrPath, fileName, content) {
    const envBase = process.env.THRUSTER_SAVE_DIR;
    let targetDir;

    if (path.isAbsolute(folderNameOrPath)) {
        targetDir = folderNameOrPath;
    } else {
        // On Windows, allow explicit D: drive via env or default to D:\ if provided
        if (process.platform === 'win32') {
            const base = envBase || 'D:\\';
            targetDir = path.join(base, folderNameOrPath);
        } else {
            // POSIX (e.g., Raspberry Pi)
            const base = envBase || path.join(os.homedir(), 'thruster-data');
            targetDir = path.join(base, folderNameOrPath);
        }
    }

    const targetPath = path.join(targetDir, fileName);
    // Ensure directory exists
    await fs.promises.mkdir(targetDir, { recursive: true });
    // Write file
    await fs.promises.writeFile(targetPath, content, { encoding: typeof content === 'string' ? 'utf8' : undefined });
    return targetPath;
}

module.exports = {
    saveToPath
};
