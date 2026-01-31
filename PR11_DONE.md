# Module 11: Google Integration

**Status**: COMPLETE

## Overview

Module 11 adds Google Drive integration to KnowBook, enabling users to import files directly from their Google Drive into project sources. This module implements OAuth 2.0 authentication, file browsing, and automatic file conversion for Google Workspace documents.

## Components Implemented

### Backend

#### 1. Google API Blueprint (`/backend/app/api/google/`)
- `__init__.py` - Blueprint initialization with route registration
- `oauth.py` - OAuth 2.0 flow endpoints
- `drive.py` - File operations endpoints

**OAuth Endpoints:**
- `GET /google/status` - Check configuration and connection status
- `GET /google/auth` - Get OAuth authorization URL
- `GET /google/callback` - Handle OAuth callback (redirect-based)
- `POST /google/disconnect` - Remove stored tokens

**Drive Endpoints:**
- `GET /google/files` - List files with pagination and folder navigation
- `POST /projects/{project_id}/sources/google-import` - Import file to sources

#### 2. Google Services (`/backend/app/services/integrations/google/`)
- `google_auth_service.py` - OAuth 2.0 authentication lifecycle
  - Token generation and refresh
  - Credential storage in `data/google_tokens.json`
  - User email retrieval via Drive API

- `google_drive_service.py` - Drive file operations
  - File listing with filtering
  - Regular file downloads
  - Google Workspace file exports (Docs→DOCX, Sheets→CSV, Slides→PPTX)

### Frontend

#### 1. API Client (`/frontend/src/lib/api/settings.ts`)
- `settingsAPI` - API key CRUD operations
- `processingSettingsAPI` - Anthropic tier configuration
- `googleDriveAPI` - Google Drive operations
  - `getStatus()` - Check connection status
  - `getAuthUrl()` - Get OAuth URL
  - `disconnect()` - Remove tokens
  - `listFiles()` - Paginated file listing
  - `importFile()` - Import to project sources

**TypeScript Interfaces:**
- `GoogleStatus` - Connection status
- `GoogleFile` - File metadata
- `GoogleFilesResponse` - Paginated response

#### 2. Google Drive Components (`/frontend/src/components/sources/`)
- `GoogleDriveTab.tsx` - Main file browser component
  - Folder navigation with breadcrumb
  - Client-side search filtering
  - Pagination with "Load More"
  - Import confirmation dialog

- `drive/DriveItem.tsx` - File/folder row component
  - Icon selection by MIME type
  - File size formatting
  - Import state indicator

- `drive/index.ts` - Barrel exports

#### 3. UI Components
- `ui/alert-dialog.tsx` - Confirmation dialog (imported from shadcn/ui)

## API Endpoints

### OAuth Flow
```
GET  /api/v1/google/status     - Check if OAuth is configured and connected
GET  /api/v1/google/auth       - Get authorization URL to redirect user
GET  /api/v1/google/callback   - OAuth callback (redirects to frontend)
POST /api/v1/google/disconnect - Remove stored tokens
```

### Drive Operations
```
GET  /api/v1/google/files                              - List files
     ?folder_id=<id>                                   - Optional folder ID
     &page_size=50                                     - Items per page
     &page_token=<token>                               - Pagination token

POST /api/v1/projects/{project_id}/sources/google-import
     {"file_id": "...", "name": "optional name"}       - Import file
```

## Data Models

### GoogleFile
```typescript
interface GoogleFile {
  id: string;
  name: string;
  mime_type: string;
  size: number | null;
  modified_time: string;
  is_folder: boolean;
  is_google_file: boolean;      // True for Docs/Sheets/Slides
  export_extension: string | null;  // ".docx", ".csv", ".pptx"
  google_type: string | null;   // "Google Doc", etc.
  icon_link: string | null;
  thumbnail_link: string | null;
}
```

### GoogleStatus
```typescript
interface GoogleStatus {
  configured: boolean;  // OAuth credentials set in .env
  connected: boolean;   // Valid tokens stored
  email: string | null; // User's Google email
}
```

## OAuth 2.0 Flow

```
1. User clicks "Connect Google Drive" in App Settings
2. Frontend calls GET /google/auth
3. Backend returns authorization URL
4. User redirects to Google, grants permission
5. Google redirects to /google/callback with auth code
6. Backend exchanges code for access + refresh tokens
7. Tokens stored in data/google_tokens.json
8. User redirected to frontend with success status
```

## Google Workspace File Exports

| Source Type | Exported As | Extension |
|-------------|-------------|-----------|
| Google Docs | DOCX | .docx |
| Google Sheets | CSV | .csv |
| Google Slides | PPTX | .pptx |

Regular files (PDF, images, audio) are downloaded directly without conversion.

## Supported File Types

**Documents:**
- PDF, TXT, DOCX, PPTX, CSV

**Images:**
- JPEG, PNG, GIF, WebP

**Audio:**
- MP3, M4A, WAV, AAC, FLAC

**Google Workspace:**
- Google Docs, Sheets, Slides (exported to standard formats)

## File Structure

```
knowbook/
├── backend/app/
│   ├── api/
│   │   ├── __init__.py (updated - registered google_bp)
│   │   └── google/
│   │       ├── __init__.py
│   │       ├── oauth.py
│   │       └── drive.py
│   └── services/integrations/google/
│       ├── __init__.py
│       ├── google_auth_service.py
│       └── google_drive_service.py
│
└── frontend/src/
    ├── lib/api/
    │   └── settings.ts (created with Google Drive API)
    └── components/
        ├── ui/
        │   └── alert-dialog.tsx (added)
        └── sources/
            ├── GoogleDriveTab.tsx
            └── drive/
                ├── index.ts
                └── DriveItem.tsx
```

## Dependencies

### Backend (requirements.txt)
- `google-auth` - Google authentication library
- `google-auth-oauthlib` - OAuth 2.0 flow helpers
- `google-api-python-client` - Google API client

### Frontend (package.json)
- `@radix-ui/react-alert-dialog` - Confirmation dialog primitive
- `axios` - HTTP client (existing)
- `@phosphor-icons/react` - Icons (existing)

## Configuration

### Environment Variables (.env)
```bash
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
```

### Google Cloud Console Setup
1. Create project at https://console.cloud.google.com
2. Enable Google Drive API
3. Create OAuth 2.0 credentials (Web application)
4. Add redirect URI: `http://localhost:5000/api/v1/google/callback`

## Testing

### Backend Verification
- All Python files pass syntax check (`python -m py_compile`)
- API blueprint registered in main `__init__.py`
- Services properly import from KnowBook patterns

### Frontend Verification
- TypeScript compilation passes without errors
- All component exports properly configured
- API types match backend response structures

## Security Considerations

- OAuth tokens stored locally, not in .env
- Client secret never exposed to frontend
- Token refresh handled automatically
- User can revoke access via Google account settings

## Features

| Feature | Description |
|---------|-------------|
| OAuth 2.0 | Secure authorization flow with refresh tokens |
| Folder Navigation | Browse Drive folders with back navigation |
| Pagination | Load more files on demand |
| Client Search | Filter files by name locally |
| File Preview | Icons based on file type |
| Workspace Export | Auto-convert Docs/Sheets/Slides |
| Import Confirmation | Dialog before importing files |

## Next Steps (Module 12)

- Additional cloud storage integrations (Dropbox, OneDrive)
- Batch import for multiple files
- File preview before import
- Sync status for previously imported files

---

## Module 11 Complete!

Module 11 successfully adds Google Drive integration to KnowBook, allowing users to connect their Google account and import files directly from Google Drive into their project sources. The implementation includes full OAuth 2.0 authentication, folder navigation, pagination, and automatic file conversion for Google Workspace documents.

**Ready to merge and move to Module 12!**
