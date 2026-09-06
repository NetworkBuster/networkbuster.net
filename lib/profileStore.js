import fs from 'fs';
import { promises as fsPromises } from 'fs';
import path from 'path';

const DATA_DIR = path.resolve(process.cwd(), 'data');
const PROFILES_DIR = path.join(DATA_DIR, 'profiles');
const FEEDBACK_DIR = path.join(DATA_DIR, 'feedback');

async function ensureDirs(){
  try {
    await fsPromises.access(DATA_DIR);
  } catch {
    await fsPromises.mkdir(DATA_DIR, { recursive: true });
  }
  try {
    await fsPromises.access(PROFILES_DIR);
  } catch {
    await fsPromises.mkdir(PROFILES_DIR, { recursive: true });
  }
  try {
    await fsPromises.access(FEEDBACK_DIR);
  } catch {
    await fsPromises.mkdir(FEEDBACK_DIR, { recursive: true });
  }
}

export async function getProfile(userId){
  await ensureDirs();
  if (!userId) return null;
  const f = path.join(PROFILES_DIR, `${userId}.json`);
  try { 
    const data = await fsPromises.readFile(f, 'utf8');
    return JSON.parse(data);
  } catch { 
    return null;
  }
}

export async function saveProfile(userId, profile){
  await ensureDirs();
  const f = path.join(PROFILES_DIR, `${userId}.json`);
  await fsPromises.writeFile(f, JSON.stringify(profile, null, 2), 'utf8');
  return profile;
}

export async function appendFeedback(feedback){
  await ensureDirs();
  const id = Date.now().toString();
  const f = path.join(FEEDBACK_DIR, `${id}.json`);
  await fsPromises.writeFile(f, JSON.stringify(feedback, null, 2), 'utf8');
  return f;
}

export default { getProfile, saveProfile, appendFeedback };
