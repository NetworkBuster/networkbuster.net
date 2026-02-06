// publishGraph.js (Raspberry Pi friendly)
// Converts SVG to PNG and prepares for io.github publishing with a fallback
// in case native 'sharp' binaries are not available on Pi.

const fs = require("fs");
const path = require("path");
let sharp;
let Jimp;

try {
  sharp = require("sharp");
} catch (e) {
  // sharp may not have prebuilt binaries for some Pi OS versions; fall back to Jimp
  try {
    Jimp = require("jimp");
  } catch (err) {
    throw new Error(
      "Neither sharp nor jimp is available. Install one to convert SVGs.",
    );
  }
}

/**
 * Convert SVG file to PNG for legible publishing
 * @param {string} svgPath - Path to the SVG file
 * @param {string} outputPath - Path to save the PNG file
 * @param {object} [options] - Optional settings: { width, height }
 * @returns {Promise<string>} - Path to the PNG file
 */
async function convertSvgToPng(svgPath, outputPath, options = {}) {
  const svgBuffer = await fs.promises.readFile(svgPath);
  if (sharp) {
    const transformer = sharp(svgBuffer).png();
    if (options.width || options.height)
      transformer.resize(options.width, options.height, { fit: "inside" });
    await transformer.toFile(outputPath);
    return outputPath;
  }
  // Fallback using Jimp: render via an SVG-to-PNG data URI using Jimp's read
  const svgDataUri =
    "data:image/svg+xml;charset=utf-8," +
    encodeURIComponent(svgBuffer.toString("utf8"));
  const image = await Jimp.read(svgDataUri);
  if (options.width || options.height)
    image.contain(
      options.width || image.bitmap.width,
      options.height || image.bitmap.height,
    );
  await image.writeAsync(outputPath);
  return outputPath;
}

// Small CLI helper for convenience on Pi
if (require.main === module) {
  (async () => {
    const argv = process.argv.slice(2);
    if (argv.length < 2) {
      console.error(
        "Usage: node publishGraph.js <input.svg> <output.png> [width] [height]",
      );
      process.exit(2);
    }
    const [inFile, outFile, w, h] = argv;
    try {
      const out = await convertSvgToPng(inFile, outFile, {
        width: w ? parseInt(w, 10) : undefined,
        height: h ? parseInt(h, 10) : undefined,
      });
      console.log("Saved:", out);
    } catch (err) {
      console.error("Conversion failed:", err.message);
      process.exit(1);
    }
  })();
}

module.exports = {
  convertSvgToPng,
};
