// publishGraph.cjs (CJS)
// Converts SVG to PNG and prepares for io.github publishing with a fallback
// in case native 'sharp' binaries are not available on Pi.

const fs = require('fs');
const path = require('path');
let sharp;
let Jimp;

try {
    sharp = require('sharp');
} catch (e) {
    try {
        Jimp = require('jimp');
    } catch (err) {
        throw new Error('Neither sharp nor jimp is available. Install one to convert SVGs.');
    }
}

async function convertSvgToPng(svgPath, outputPath, options = {}) {
    const svgBuffer = await fs.promises.readFile(svgPath);
    if (sharp) {
        const transformer = sharp(svgBuffer).png();
        if (options.width || options.height) transformer.resize(options.width, options.height, { fit: 'inside' });
        await transformer.toFile(outputPath);
        return outputPath;
    }
    const svgDataUri = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svgBuffer.toString('utf8'));
    const image = await Jimp.read(svgDataUri);
    if (options.width || options.height) image.contain(options.width || image.bitmap.width, options.height || image.bitmap.height);
    await image.writeAsync(outputPath);
    return outputPath;
}

// Convert an SVG string to a PNG Buffer (in-memory) - better for API responses
async function convertSvgStringToPngBuffer(svgString, options = {}) {
    const svgBuffer = Buffer.from(svgString, 'utf8');
    if (sharp) {
        let img = sharp(svgBuffer).png();
        if (options.width || options.height) img = img.resize(options.width, options.height, { fit: 'inside' });
        return await img.toBuffer();
    }
    // Jimp fallback
    const svgDataUri = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svgString);
    const image = await Jimp.read(svgDataUri);
    if (options.width || options.height) image.contain(options.width || image.bitmap.width, options.height || image.bitmap.height);
    return await image.getBufferAsync(Jimp.MIME_PNG);
}

if (require.main === module) {
    (async () => {
        const argv = process.argv.slice(2);
        if (argv.length < 2) {
            console.error('Usage: node publishGraph.cjs <input.svg> <output.png> [width] [height]');
            process.exit(2);
        }
        const [inFile, outFile, w, h] = argv;
        try {
            const out = await convertSvgToPng(inFile, outFile, { width: w ? parseInt(w, 10) : undefined, height: h ? parseInt(h, 10) : undefined });
            console.log('Saved:', out);
        } catch (err) {
            console.error('Conversion failed:', err.message);
            process.exit(1);
        }
    })();
}

module.exports = { convertSvgToPng };
