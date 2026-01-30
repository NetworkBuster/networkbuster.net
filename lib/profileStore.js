import fs from 'fs';
import path from 'path';

const DATA_DIR = path.resolve(process.cwd(), 'data');
const PROFILES_DIR = path.join(DATA_DIR, 'profiles');
const FEEDBACK_DIR = path.join(DATA_DIR, 'feedback');

function ensureDirs(){
  if (!fs.existsSync(DATA_DIR)) fs.mkdirSync(DATA_DIR);
  if (!fs.existsSync(PROFILES_DIR)) fs.mkdirSync(PROFILES_DIR);
  if (!fs.existsSync(FEEDBACK_DIR)) fs.mkdirSync(FEEDBACK_DIR);
}

export function getProfile(userId){
  ensureDirs();
  if (!userId) return null;
  const f = path.join(PROFILES_DIR, `${userId}.json`);
  if (!fs.existsSync(f)) return null;
  try { return JSON.parse(fs.readFileSync(f,'utf8')); } catch { return null }
}

export function saveProfile(userId, profile){
  ensureDirs();
  const f = path.join(PROFILES_DIR, `${userId}.json`);
  fs.writeFileSync(f, JSON.stringify(profile, null, 2), 'utf8');
  return profile;
}

export function appendFeedback(feedback){
  ensureDirs();
  const id = Date.now().toString();
  const f = path.join(FEEDBACK_DIR, `${id}.json`);
  fs.writeFileSync(f, JSON.stringify(feedback, null, 2), 'utf8');
  return f;
}

export default { getProfile, saveProfile, appendFeedback };
