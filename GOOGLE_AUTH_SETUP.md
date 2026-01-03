# Google Authentication Setup Guide

## Overview
This guide walks you through setting up Google-only authentication for NetworkBuster with Excel user registration tracking.

## Files Modified/Created
- `web-app/auth.html` - Updated to Google-only sign-in
- `web-app/auth-callback.html` - OAuth callback handler
- `auth-server.js` - Backend server for Excel recording
- `package.json` - Added required dependencies

## Setup Instructions

### 1. Create Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Navigate to **APIs & Services** → **Credentials**
4. Click **Create Credentials** → **OAuth client ID**
5. Select **Web application**
6. Add authorized JavaScript origins:
   - `http://localhost:5173`
   - `http://localhost:3000`
   - `https://your-domain.com` (production)
7. Add authorized redirect URIs:
   - `http://localhost:5173/web-app/auth-callback.html`
   - `https://your-domain.com/web-app/auth-callback.html` (production)
8. Copy the **Client ID**

### 2. Configure the Application

Update the Google Client ID in two files:

**File 1: `web-app/auth.html`**
```javascript
const GOOGLE_CLIENT_ID = 'YOUR_ACTUAL_CLIENT_ID.apps.googleusercontent.com';
```

**File 2: `auth-server.js`**
```javascript
const GOOGLE_CLIENT_ID = process.env.GOOGLE_CLIENT_ID || 'YOUR_ACTUAL_CLIENT_ID.apps.googleusercontent.com';
```

Or set environment variable:
```bash
set GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
```

### 3. Install Dependencies

```bash
npm install
```

### 4. Start the Auth Server

```bash
npm run auth-server
```

The server runs on port 3002 by default.

### 5. Excel Files Location

User data is automatically saved to:
- `data/registered_users.xlsx` - All registered users
- `data/login_history.xlsx` - Complete login history

## Excel Data Structure

### registered_users.xlsx
| Column | Description |
|--------|-------------|
| Google ID | Unique Google account identifier |
| Email | User's email address |
| Name | Display name from Google |
| Picture URL | Profile picture URL |
| First Login | Timestamp of first login |
| Last Login | Most recent login |
| Login Count | Total number of logins |
| Status | Account status (Active) |

### login_history.xlsx
| Column | Description |
|--------|-------------|
| Login ID | Unique login event ID |
| Google ID | User's Google ID |
| Email | User's email |
| Name | Display name |
| Login Time | When login occurred |
| IP Address | User's IP address |
| User Agent | Browser/device info |

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/google` | POST | Authenticate with Google |
| `/api/admin/users` | GET | List all users (JSON) |
| `/api/admin/logins` | GET | Get login history (JSON) |
| `/api/admin/stats` | GET | User statistics |
| `/api/admin/users/download` | GET | Download users Excel |
| `/api/admin/logins/download` | GET | Download logins Excel |
| `/health` | GET | Server health check |

## Running Both Servers

To run both the main app and auth server:

```bash
npm run dev
```

Or run separately:
```bash
# Terminal 1 - Main app
npm start

# Terminal 2 - Auth server
npm run auth-server
```

## Security Notes

1. **Production**: Always use HTTPS
2. **Client ID**: Keep your Google Client ID secure
3. **CORS**: Update allowed origins in `auth-server.js` for production
4. **Admin Endpoints**: Consider adding authentication to admin endpoints

## Troubleshooting

### "popup blocked" error
- Ensure popups are allowed for your domain
- The Google Sign-In button should work without popup for most cases

### Token verification fails
- Check if Google Client ID matches in both frontend and backend
- Ensure the OAuth consent screen is properly configured

### Excel files not created
- Check write permissions for the `data/` directory
- Ensure xlsx package is installed correctly
