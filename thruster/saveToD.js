// thruster/saveToD backend feature
// This module saves data to a folder on the D: drive

const fs = require('fs');
const path = require('path');

/**
 * Save content to a specified folder on D: drive.
 * @param {string} folderName - The folder name under D:\
 * @param {string} fileName - The file name to save
 * @param {string} content - The content to write
 * @returns {Promise<string>} - Path to the saved file
 */
async function saveToDFolder(folderName, fileName, content) {
    const targetDir = path.join('D:\\', folderName);
    const targetPath = path.join(targetDir, fileName);
    // Ensure directory exists
    await fs.promises.mkdir(targetDir, { recursive: true });
    // Write file
    await fs.promises.writeFile(targetPath, content, 'utf8');
    return targetPath;
}

module.exports = {
    saveToDFolder
};
