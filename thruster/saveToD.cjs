// thruster/saveToD backend feature (CJS)
// Cross-platform save helper with configurable base directory

const fs = require("fs");
const path = require("path");
const os = require("os");

async function saveToPath(folderNameOrPath, fileName, content) {
  const envBase = process.env.THRUSTER_SAVE_DIR;
  let targetDir;

  if (path.isAbsolute(folderNameOrPath)) {
    targetDir = folderNameOrPath;
  } else {
    if (process.platform === "win32") {
      const base = envBase || "D:\\";
      targetDir = path.join(base, folderNameOrPath);
    } else {
      const base = envBase || path.join(os.homedir(), "thruster-data");
      targetDir = path.join(base, folderNameOrPath);
    }
  }

  const targetPath = path.join(targetDir, fileName);
  await fs.promises.mkdir(targetDir, { recursive: true });
  await fs.promises.writeFile(targetPath, content, {
    encoding: typeof content === "string" ? "utf8" : undefined,
  });
  return targetPath;
}

module.exports = {
  saveToPath,
};
