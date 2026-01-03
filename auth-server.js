/**
 * Authentication Server for NetworkBuster
 * Handles Google OAuth and records user registrations to Excel files
 */

import express from 'express';
import cors from 'cors';
import { OAuth2Client } from 'google-auth-library';
import XLSX from 'xlsx';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.AUTH_PORT || 3002;

// Configuration
const GOOGLE_CLIENT_ID = process.env.GOOGLE_CLIENT_ID || 'YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com';
const USERS_EXCEL_FILE = path.join(__dirname, 'data', 'registered_users.xlsx');
const LOGINS_EXCEL_FILE = path.join(__dirname, 'data', 'login_history.xlsx');

// Initialize Google OAuth client
const googleClient = new OAuth2Client(GOOGLE_CLIENT_ID);

// Middleware
app.use(cors({
    origin: ['http://localhost:5173', 'http://localhost:3000', 'http://localhost:3001', 'http://127.0.0.1:5173'],
    credentials: true
}));
app.use(express.json());

// Ensure data directory exists
function ensureDataDirectory() {
    const dataDir = path.join(__dirname, 'data');
    if (!fs.existsSync(dataDir)) {
        fs.mkdirSync(dataDir, { recursive: true });
        console.log('📁 Created data directory');
    }
}

// Initialize or load Excel workbook for users
function getOrCreateUsersWorkbook() {
    if (fs.existsSync(USERS_EXCEL_FILE)) {
        return XLSX.readFile(USERS_EXCEL_FILE);
    }
    
    // Create new workbook with headers
    const wb = XLSX.utils.book_new();
    const headers = [
        ['Google ID', 'Email', 'Name', 'Picture URL', 'First Login', 'Last Login', 'Login Count', 'Status']
    ];
    const ws = XLSX.utils.aoa_to_sheet(headers);
    
    // Set column widths
    ws['!cols'] = [
        { wch: 25 },  // Google ID
        { wch: 35 },  // Email
        { wch: 25 },  // Name
        { wch: 50 },  // Picture URL
        { wch: 22 },  // First Login
        { wch: 22 },  // Last Login
        { wch: 12 },  // Login Count
        { wch: 12 }   // Status
    ];
    
    XLSX.utils.book_append_sheet(wb, ws, 'Users');
    XLSX.writeFile(wb, USERS_EXCEL_FILE);
    console.log('📊 Created users Excel file');
    return wb;
}

// Initialize or load Excel workbook for login history
function getOrCreateLoginsWorkbook() {
    if (fs.existsSync(LOGINS_EXCEL_FILE)) {
        return XLSX.readFile(LOGINS_EXCEL_FILE);
    }
    
    const wb = XLSX.utils.book_new();
    const headers = [
        ['Login ID', 'Google ID', 'Email', 'Name', 'Login Time', 'IP Address', 'User Agent']
    ];
    const ws = XLSX.utils.aoa_to_sheet(headers);
    
    ws['!cols'] = [
        { wch: 15 },  // Login ID
        { wch: 25 },  // Google ID
        { wch: 35 },  // Email
        { wch: 25 },  // Name
        { wch: 22 },  // Login Time
        { wch: 15 },  // IP Address
        { wch: 60 }   // User Agent
    ];
    
    XLSX.utils.book_append_sheet(wb, ws, 'Login History');
    XLSX.writeFile(wb, LOGINS_EXCEL_FILE);
    console.log('📊 Created login history Excel file');
    return wb;
}

// Find user by Google ID in Excel
function findUserByGoogleId(googleId) {
    const wb = getOrCreateUsersWorkbook();
    const ws = wb.Sheets['Users'];
    const data = XLSX.utils.sheet_to_json(ws, { header: 1 });
    
    for (let i = 1; i < data.length; i++) {
        if (data[i][0] === googleId) {
            return {
                rowIndex: i,
                googleId: data[i][0],
                email: data[i][1],
                name: data[i][2],
                picture: data[i][3],
                firstLogin: data[i][4],
                lastLogin: data[i][5],
                loginCount: data[i][6],
                status: data[i][7]
            };
        }
    }
    return null;
}

// Add or update user in Excel
function saveUserToExcel(userData, isNewUser, ipAddress, userAgent) {
    ensureDataDirectory();
    
    const now = new Date().toISOString();
    const wb = getOrCreateUsersWorkbook();
    const ws = wb.Sheets['Users'];
    const data = XLSX.utils.sheet_to_json(ws, { header: 1 });
    
    if (isNewUser) {
        // Add new user row
        const newRow = [
            userData.googleId,
            userData.email,
            userData.name,
            userData.picture || '',
            now,           // First Login
            now,           // Last Login
            1,             // Login Count
            'Active'       // Status
        ];
        data.push(newRow);
        console.log(`✅ New user registered: ${userData.email}`);
    } else {
        // Update existing user
        const existingUser = findUserByGoogleId(userData.googleId);
        if (existingUser) {
            const rowIndex = existingUser.rowIndex;
            data[rowIndex][2] = userData.name;  // Update name (might change)
            data[rowIndex][3] = userData.picture || data[rowIndex][3];  // Update picture
            data[rowIndex][5] = now;  // Update last login
            data[rowIndex][6] = (parseInt(data[rowIndex][6]) || 0) + 1;  // Increment login count
            console.log(`🔄 User login: ${userData.email} (Count: ${data[rowIndex][6]})`);
        }
    }
    
    // Write back to file
    const newWs = XLSX.utils.aoa_to_sheet(data);
    newWs['!cols'] = ws['!cols'];
    wb.Sheets['Users'] = newWs;
    XLSX.writeFile(wb, USERS_EXCEL_FILE);
    
    // Also record login in history
    recordLoginHistory(userData, ipAddress, userAgent);
    
    return true;
}

// Record login to history Excel
function recordLoginHistory(userData, ipAddress, userAgent) {
    const wb = getOrCreateLoginsWorkbook();
    const ws = wb.Sheets['Login History'];
    const data = XLSX.utils.sheet_to_json(ws, { header: 1 });
    
    const loginId = `L${Date.now()}`;
    const now = new Date().toISOString();
    
    const newRow = [
        loginId,
        userData.googleId,
        userData.email,
        userData.name,
        now,
        ipAddress || 'Unknown',
        userAgent || 'Unknown'
    ];
    
    data.push(newRow);
    
    const newWs = XLSX.utils.aoa_to_sheet(data);
    newWs['!cols'] = ws['!cols'];
    wb.Sheets['Login History'] = newWs;
    XLSX.writeFile(wb, LOGINS_EXCEL_FILE);
}

// Verify Google Token
async function verifyGoogleToken(token) {
    try {
        const ticket = await googleClient.verifyIdToken({
            idToken: token,
            audience: GOOGLE_CLIENT_ID
        });
        return ticket.getPayload();
    } catch (error) {
        console.error('Token verification failed:', error.message);
        return null;
    }
}

// Routes

// Health check
app.get('/health', (req, res) => {
    res.json({ status: 'ok', service: 'NetworkBuster Auth Server', timestamp: new Date().toISOString() });
});

// Google authentication endpoint
app.post('/api/auth/google', async (req, res) => {
    try {
        const { googleId, email, name, picture, token } = req.body;
        
        if (!googleId || !email) {
            return res.status(400).json({ error: 'Missing required fields: googleId, email' });
        }
        
        // Optionally verify token with Google (if provided)
        if (token && GOOGLE_CLIENT_ID !== 'YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com') {
            const payload = await verifyGoogleToken(token);
            if (!payload) {
                return res.status(401).json({ error: 'Invalid Google token' });
            }
        }
        
        // Get request info
        const ipAddress = req.ip || req.connection.remoteAddress || req.headers['x-forwarded-for'];
        const userAgent = req.headers['user-agent'];
        
        // Check if user exists
        const existingUser = findUserByGoogleId(googleId);
        const isNewUser = !existingUser;
        
        // Save to Excel
        const userData = { googleId, email, name, picture };
        saveUserToExcel(userData, isNewUser, ipAddress, userAgent);
        
        res.json({
            success: true,
            isNewUser,
            message: isNewUser ? 'Account created successfully' : 'Welcome back!',
            user: {
                googleId,
                email,
                name,
                picture,
                loginCount: existingUser ? (parseInt(existingUser.loginCount) || 0) + 1 : 1
            }
        });
        
    } catch (error) {
        console.error('Auth error:', error);
        res.status(500).json({ error: 'Authentication failed', details: error.message });
    }
});

// Get all users (admin endpoint)
app.get('/api/admin/users', (req, res) => {
    try {
        const wb = getOrCreateUsersWorkbook();
        const ws = wb.Sheets['Users'];
        const data = XLSX.utils.sheet_to_json(ws);
        res.json({ users: data, total: data.length });
    } catch (error) {
        res.status(500).json({ error: 'Failed to fetch users' });
    }
});

// Get login history (admin endpoint)
app.get('/api/admin/logins', (req, res) => {
    try {
        const wb = getOrCreateLoginsWorkbook();
        const ws = wb.Sheets['Login History'];
        const data = XLSX.utils.sheet_to_json(ws);
        res.json({ logins: data, total: data.length });
    } catch (error) {
        res.status(500).json({ error: 'Failed to fetch login history' });
    }
});

// Download users Excel file
app.get('/api/admin/users/download', (req, res) => {
    if (fs.existsSync(USERS_EXCEL_FILE)) {
        res.download(USERS_EXCEL_FILE, 'registered_users.xlsx');
    } else {
        res.status(404).json({ error: 'Users file not found' });
    }
});

// Download login history Excel file
app.get('/api/admin/logins/download', (req, res) => {
    if (fs.existsSync(LOGINS_EXCEL_FILE)) {
        res.download(LOGINS_EXCEL_FILE, 'login_history.xlsx');
    } else {
        res.status(404).json({ error: 'Login history file not found' });
    }
});

// Statistics endpoint
app.get('/api/admin/stats', (req, res) => {
    try {
        const usersWb = getOrCreateUsersWorkbook();
        const usersWs = usersWb.Sheets['Users'];
        const users = XLSX.utils.sheet_to_json(usersWs);
        
        const loginsWb = getOrCreateLoginsWorkbook();
        const loginsWs = loginsWb.Sheets['Login History'];
        const logins = XLSX.utils.sheet_to_json(loginsWs);
        
        // Calculate stats
        const today = new Date().toISOString().split('T')[0];
        const todayLogins = logins.filter(l => l['Login Time'] && l['Login Time'].startsWith(today)).length;
        
        res.json({
            totalUsers: users.length,
            totalLogins: logins.length,
            todayLogins,
            activeUsers: users.filter(u => u.Status === 'Active').length
        });
    } catch (error) {
        res.status(500).json({ error: 'Failed to fetch statistics' });
    }
});

// Initialize and start server
ensureDataDirectory();
getOrCreateUsersWorkbook();
getOrCreateLoginsWorkbook();

app.listen(PORT, () => {
    console.log(`
🔐 NetworkBuster Auth Server
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📍 Running on: http://localhost:${PORT}
📊 Users Excel: ${USERS_EXCEL_FILE}
📊 Logins Excel: ${LOGINS_EXCEL_FILE}

Endpoints:
  POST /api/auth/google     - Google authentication
  GET  /api/admin/users     - List all users
  GET  /api/admin/logins    - Login history
  GET  /api/admin/stats     - Statistics
  GET  /health              - Health check
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    `);
});

export default app;
