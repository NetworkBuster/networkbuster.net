// thruster/combustion backend feature
// This module provides combustion logic for the thruster backend

const { exec } = require('child_process');

/**
 * Run a git command and return its output.
 * @param {string} command - The git command to run (e.g., 'status', 'log').
 * @returns {Promise<string>} - Output from the git command.
 */
function runGitCommand(command) {
    return new Promise((resolve, reject) => {
        exec(`git ${command}`, { cwd: process.cwd() }, (error, stdout, stderr) => {
            if (error) {
                reject(stderr || error.message);
            } else {
                resolve(stdout);
            }
        });
    });
}

/**
 * Example combustion logic: get current git status.
 * @returns {Promise<string>} - Git status output.
 */
async function combustionStatus() {
    return await runGitCommand('status');
}

module.exports = {
    runGitCommand,
    combustionStatus
};
