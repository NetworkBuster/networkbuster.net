// publishGraph.js
// Converts SVG to PNG and prepares for io.github publishing

const fs = require('fs');
const path = require('path');
const sharp = require('sharp');

/**
 * Convert SVG file to PNG for legible publishing
 * @param {string} svgPath - Path to the SVG file
 * @param {string} outputPath - Path to save the PNG file
 * @returns {Promise<string>} - Path to the PNG file
 */
async function convertSvgToPng(svgPath, outputPath) {
    const svgBuffer = await fs.promises.readFile(svgPath);
    await sharp(svgBuffer)
        .png()
        .toFile(outputPath);
    return outputPath;
}

// Example usage:
// convertSvgToPng('path/to/input.svg', 'path/to/output.png')
//   .then(console.log)
//   .catch(console.error);

module.exports = {
    convertSvgToPng
};
