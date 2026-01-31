# Module 10: Studio - Media & Code

**Status**: COMPLETE

## Overview

Module 10 completes the Studio panel with media generation and code generation capabilities. This module enables users to generate rich media content including Audio Overviews, Videos, Websites, UI Components, Ad Creatives, Email Templates, and Social Media Posts from their uploaded sources. This is the final Studio module, bringing the total to 18 content generation types across Modules 7-10.

## Components Implemented

### Backend

#### 1. Studio API Endpoints (`/backend/app/api/studio/`)
- `audio.py` - Audio overview generation endpoints (ElevenLabs TTS)
- `videos.py` - Video generation endpoints (Google Veo 2.0)
- `websites.py` - Multi-page website generation endpoints
- `components.py` - UI component code generation endpoints
- `ads.py` - Ad creative image generation endpoints
- `emails.py` - Email template generation endpoints
- `social_posts.py` - Social media post generation endpoints

Each endpoint module provides:
- `POST /studio/{type}` - Start generation job
- `GET /studio/{type}-jobs/{job_id}` - Poll job status
- `GET /studio/{type}-jobs` - List all jobs
- Additional endpoints for serving generated files (audio, video, images, etc.)

#### 2. Studio Services (`/backend/app/services/studio_services/`)
- `audio_service.py` - Audio generation service
  - Converts source content to podcast-style audio overview
  - Uses ElevenLabs TTS with professional voices
  - Supports multiple voice options and audio formats

- `video_service.py` - Video generation service
  - Generates videos using Google Veo 2.0
  - Creates explainer videos from source content
  - Supports multiple video formats and durations
  - Long-running jobs (10-20 minutes) with extended polling

- `website_service.py` - Website generation service
  - Generates multi-page responsive websites
  - Creates HTML, CSS, and JavaScript files
  - Supports navigation, styling, and interactivity
  - Downloadable as ZIP archive

- `component_service.py` - UI component generation service
  - Generates React/Vue/Angular component code
  - Includes TypeScript definitions
  - Supports multiple UI frameworks

- `ad_service.py` - Ad creative generation service
  - Uses Gemini Imagen for image generation
  - Creates ad creatives for various platforms
  - Supports multiple sizes and formats

- `email_service.py` - Email template generation service
  - Generates HTML email templates
  - Responsive design with inline CSS
  - Includes preview and download functionality

- `social_post_service.py` - Social media post generation service
  - Generates platform-specific content
  - Supports Twitter, LinkedIn, Facebook, Instagram
  - Creates hashtags and engagement hooks

#### 3. Job Management (`/backend/app/services/studio_services/jobs/`)
- `audio_jobs.py` - CRUD operations for audio jobs
- `video_jobs.py` - CRUD operations for video jobs
- `website_jobs.py` - CRUD operations for website jobs
- `component_jobs.py` - CRUD operations for component jobs
- `ad_jobs.py` - CRUD operations for ad jobs
- `email_jobs.py` - CRUD operations for email jobs
- `social_post_jobs.py` - CRUD operations for social post jobs

#### 4. Tool Definitions (`/backend/app/services/tools/studio_tools/`)
- `audio_tool.json` - Audio script generation tool
- `video_tool.json` - Video generation tool
- `website_tool.json` - Website page generation tool
- `component_tool.json` - Component code generation tool
- `ad_tool.json` - Ad creative generation tool
- `email_tool.json` - Email template generation tool
- `social_post_tool.json` - Social post generation tool

#### 5. Prompt Configurations (`/backend/data/prompts/`)
- `audio_prompt.json` - System prompt for audio script generation
- `video_prompt.json` - System prompt for video generation
- `website_prompt.json` - System prompt for website generation
- `component_prompt.json` - System prompt for component generation
- `ad_prompt.json` - System prompt for ad creative generation
- `email_prompt.json` - System prompt for email template generation
- `social_post_prompt.json` - System prompt for social post generation

### Frontend

#### 1. API Client Layer (`/frontend/src/lib/api/studio/`)
- `audio.ts` - Audio API client with types and polling
  - `AudioJob` interface with audio_url, duration, voice settings
  - Supports ElevenLabs status check

- `videos.ts` - Video API client
  - `VideoJob` interface with videos array, generation status
  - Extended polling intervals for long-running video generation

- `websites.ts` - Website API client
  - `WebsitePage` interface with html, css, js content
  - `WebsiteJob` interface with pages array and download URL

- `components.ts` - Component API client
  - `ComponentJob` interface with code, language, framework

- `ads.ts` - Ad creative API client
  - `AdJob` interface with image_url, dimensions, platform

- `emails.ts` - Email template API client
  - `EmailJob` interface with html_content, sections, preview

- `social-posts.ts` - Social post API client
  - `SocialPost` interface with platform, content, hashtags
  - `SocialPostJob` interface with posts array

Updated `index.ts` to re-export all Module 10 APIs and types.

#### 2. Audio Components (`/frontend/src/components/studio/audio/`)
- `useAudioGeneration.ts` - Generation hook with ElevenLabs status check
- `AudioProgressIndicator.tsx` - Progress with red theme
- `AudioListItem.tsx` - Inline audio player with play/pause/download
- `index.ts` - Barrel exports

Note: Audio uses inline player in list item (no separate modal needed)

#### 3. Video Components (`/frontend/src/components/studio/video/`)
- `useVideoGeneration.ts` - Generation hook with extended polling
- `VideoProgressIndicator.tsx` - Progress with rose theme
- `VideoListItem.tsx` - List item showing video count and duration
- `VideoViewer.tsx` - Video player with playback controls
- `VideoViewerModal.tsx` - Modal wrapper with download
- `index.ts` - Barrel exports

#### 4. Website Components (`/frontend/src/components/studio/website/`)
- `useWebsiteGeneration.ts` - Generation hook
- `WebsiteProgressIndicator.tsx` - Progress with cyan theme
- `WebsiteListItem.tsx` - List item showing page count
- `WebsiteViewer.tsx` - Multi-page website preview with iframe
- `WebsiteViewerModal.tsx` - Modal wrapper with ZIP download
- `index.ts` - Barrel exports

#### 5. Component Components (`/frontend/src/components/studio/components/`)
- `useComponentGeneration.ts` - Generation hook
- `ComponentProgressIndicator.tsx` - Progress with sky theme
- `ComponentListItem.tsx` - List item showing framework and language
- `ComponentViewer.tsx` - Syntax-highlighted code viewer
- `ComponentViewerModal.tsx` - Modal with copy/download functionality
- `index.ts` - Barrel exports

#### 6. Ad Components (`/frontend/src/components/studio/ads/`)
- `useAdGeneration.ts` - Generation hook with Gemini status check
- `AdProgressIndicator.tsx` - Progress with fuchsia theme
- `AdListItem.tsx` - List item showing ad dimensions
- `AdViewerModal.tsx` - Image viewer with download
- `index.ts` - Barrel exports

#### 7. Email Components (`/frontend/src/components/studio/email/`)
- `useEmailGeneration.ts` - Generation hook with Gemini status check
- `EmailProgressIndicator.tsx` - Progress with lime theme
- `EmailListItem.tsx` - List item showing template name
- `EmailViewerModal.tsx` - HTML email preview with download
- `index.ts` - Barrel exports

#### 8. Social Post Components (`/frontend/src/components/studio/social/`)
- `useSocialPostGeneration.ts` - Generation hook
- `SocialPostProgressIndicator.tsx` - Progress with yellow theme
- `SocialPostListItem.tsx` - List item showing post count by platform
- `SocialPostViewerModal.tsx` - Multi-platform post viewer with copy
- `index.ts` - Barrel exports

#### 9. Updated Core Components
- `types.ts` - Added all Module 10 items to StudioItemId
  - Added generationOptions entries with icons
- `index.ts` - Added exports for all new component directories
- `StudioPanel.tsx` - Integrated all 7 new generation hooks
- `StudioProgressIndicators.tsx` - Added all 7 progress indicators (now 18 total)
- `StudioGeneratedContent.tsx` - Added all 7 list item renderers (now 18 total)
- `StudioModals.tsx` - Added all 6 viewer modals (audio uses inline player)

## API Endpoints

### Audio Endpoints
- `POST /api/v1/projects/{project_id}/studio/audio` - Start generation
- `GET /api/v1/projects/{project_id}/studio/audio-jobs/{job_id}` - Get job status
- `GET /api/v1/projects/{project_id}/studio/audio-jobs` - List jobs
- `GET /api/v1/projects/{project_id}/studio/audio/{job_id}/file` - Serve audio file

### Video Endpoints
- `POST /api/v1/projects/{project_id}/studio/video` - Start generation
- `GET /api/v1/projects/{project_id}/studio/video-jobs/{job_id}` - Get job status
- `GET /api/v1/projects/{project_id}/studio/video-jobs` - List jobs
- `GET /api/v1/projects/{project_id}/studio/videos/{job_id}/{filename}` - Serve video file

### Website Endpoints
- `POST /api/v1/projects/{project_id}/studio/website` - Start generation
- `GET /api/v1/projects/{project_id}/studio/website-jobs/{job_id}` - Get job status
- `GET /api/v1/projects/{project_id}/studio/website-jobs` - List jobs
- `GET /api/v1/projects/{project_id}/studio/websites/{job_id}/download` - Download ZIP
- `GET /api/v1/projects/{project_id}/studio/websites/{job_id}/preview/{page}` - Preview page

### Component Endpoints
- `POST /api/v1/projects/{project_id}/studio/component` - Start generation
- `GET /api/v1/projects/{project_id}/studio/component-jobs/{job_id}` - Get job status
- `GET /api/v1/projects/{project_id}/studio/component-jobs` - List jobs

### Ad Endpoints
- `POST /api/v1/projects/{project_id}/studio/ads` - Start generation
- `GET /api/v1/projects/{project_id}/studio/ad-jobs/{job_id}` - Get job status
- `GET /api/v1/projects/{project_id}/studio/ad-jobs` - List jobs
- `GET /api/v1/projects/{project_id}/studio/ads/{filename}` - Serve ad image

### Email Endpoints
- `POST /api/v1/projects/{project_id}/studio/email` - Start generation
- `GET /api/v1/projects/{project_id}/studio/email-jobs/{job_id}` - Get job status
- `GET /api/v1/projects/{project_id}/studio/email-jobs` - List jobs

### Social Post Endpoints
- `POST /api/v1/projects/{project_id}/studio/social-posts` - Start generation
- `GET /api/v1/projects/{project_id}/studio/social-post-jobs/{job_id}` - Get job status
- `GET /api/v1/projects/{project_id}/studio/social-post-jobs` - List jobs

## Data Models

### Audio Job
```typescript
interface AudioJob {
  id: string;
  source_id: string;
  audio_url: string | null;
  duration_seconds: number | null;
  voice_id: string;
  voice_name: string;
  format: 'mp3' | 'wav';
  // ... common job fields
}
```

### Video Job
```typescript
interface VideoInfo {
  filename: string;
  url: string;
  duration_seconds: number;
  resolution: string;
}

interface VideoJob {
  id: string;
  source_id: string;
  videos: VideoInfo[];
  video_count: number;
  total_duration: number;
  // ... common job fields
}
```

### Website Job
```typescript
interface WebsitePage {
  name: string;
  title: string;
  html: string;
  css: string;
  js: string;
}

interface WebsiteJob {
  id: string;
  source_id: string;
  site_name: string;
  pages: WebsitePage[];
  page_count: number;
  download_url: string | null;
  // ... common job fields
}
```

### Component Job
```typescript
interface ComponentJob {
  id: string;
  source_id: string;
  component_name: string;
  framework: 'react' | 'vue' | 'angular' | 'svelte';
  language: 'typescript' | 'javascript';
  code: string;
  props_interface: string | null;
  // ... common job fields
}
```

### Ad Job
```typescript
interface AdJob {
  id: string;
  topic: string;
  platform: 'facebook' | 'instagram' | 'google' | 'linkedin';
  dimensions: { width: number; height: number };
  image_url: string | null;
  image_prompt: string | null;
  // ... common job fields
}
```

### Email Job
```typescript
interface EmailSection {
  name: string;
  content: string;
}

interface EmailJob {
  id: string;
  source_id: string;
  template_name: string;
  subject_line: string;
  html_content: string | null;
  sections: EmailSection[];
  color_scheme: { primary: string; secondary: string; accent: string };
  // ... common job fields
}
```

### Social Post Job
```typescript
interface SocialPost {
  platform: 'twitter' | 'linkedin' | 'facebook' | 'instagram';
  content: string;
  hashtags: string[];
  character_count: number;
}

interface SocialPostJob {
  id: string;
  topic: string;
  posts: SocialPost[];
  post_count: number;
  // ... common job fields
}
```

## Dependencies

### Frontend (package.json)
- Existing React and TypeScript dependencies
- No new external dependencies required

### Backend (requirements.txt)
- `elevenlabs` - ElevenLabs TTS API client
- `google-generativeai` - Google Gemini API (for Veo 2.0 and Imagen)
- Existing Claude API for content analysis

### External API Requirements
- **ElevenLabs API Key** - Required for audio generation
- **Google Gemini API Key** - Required for video, ad, and email image generation

## Architecture Notes

### Audio Generation Pattern
```
User triggers Audio generation
    → Check ElevenLabs API status
    → POST /studio/audio with source_id
    → Claude generates podcast-style script
    → ElevenLabs TTS converts script to audio
    → Audio file saved to project storage
    → Frontend renders inline audio player
    → User can play, pause, download
```

### Video Generation Pattern
```
User triggers Video generation
    → Check Gemini API status
    → POST /studio/video with source_id
    → Claude generates video script and prompts
    → Google Veo 2.0 generates video (10-20 min)
    → Extended polling with exponential backoff
    → Video files saved to project storage
    → Frontend renders video player with controls
```

### Website Generation Pattern
```
User triggers Website generation
    → POST /studio/website with source_id
    → Claude analyzes content structure
    → Generates multi-page HTML/CSS/JS
    → Files packaged as downloadable ZIP
    → Frontend shows page preview with iframe
    → User can navigate pages, download ZIP
```

### Component Generation Pattern
```
User triggers Component generation
    → POST /studio/component with source_id
    → Claude generates framework-specific code
    → Returns typed component with props
    → Frontend shows syntax-highlighted code
    → User can copy or download code
```

### Ad/Email/Social Generation Pattern
```
User triggers generation
    → Check Gemini API status (if images needed)
    → POST /studio/{type} with topic/source
    → Claude generates content structure
    → Gemini generates images (ads, emails)
    → Frontend renders preview with download/copy
```

### Color Themes
- Audio: Red (`red-500`, `red-600`)
- Video: Rose (`rose-500`, `rose-600`)
- Website: Cyan (`cyan-500`, `cyan-600`)
- Component: Sky (`sky-500`, `sky-600`)
- Ad: Fuchsia (`fuchsia-500`, `fuchsia-600`)
- Email: Lime (`lime-500`, `lime-600`)
- Social Posts: Yellow (`yellow-500`, `yellow-600`)

## File Structure

```
knowbook/
├── backend/app/
│   ├── api/studio/
│   │   ├── __init__.py (updated)
│   │   ├── audio.py
│   │   ├── videos.py
│   │   ├── websites.py
│   │   ├── components.py
│   │   ├── ads.py
│   │   ├── emails.py
│   │   └── social_posts.py
│   ├── services/studio_services/
│   │   ├── __init__.py
│   │   ├── studio_index_service.py (updated)
│   │   ├── audio_service.py
│   │   ├── video_service.py
│   │   ├── website_service.py
│   │   ├── component_service.py
│   │   ├── ad_service.py
│   │   ├── email_service.py
│   │   ├── social_post_service.py
│   │   └── jobs/
│   │       ├── audio_jobs.py
│   │       ├── video_jobs.py
│   │       ├── website_jobs.py
│   │       ├── component_jobs.py
│   │       ├── ad_jobs.py
│   │       ├── email_jobs.py
│   │       └── social_post_jobs.py
│   ├── services/tools/studio_tools/
│   │   ├── audio_tool.json
│   │   ├── video_tool.json
│   │   ├── website_tool.json
│   │   ├── component_tool.json
│   │   ├── ad_tool.json
│   │   ├── email_tool.json
│   │   └── social_post_tool.json
│
├── backend/data/prompts/
│   ├── audio_prompt.json
│   ├── video_prompt.json
│   ├── website_prompt.json
│   ├── component_prompt.json
│   ├── ad_prompt.json
│   ├── email_prompt.json
│   └── social_post_prompt.json
│
└── frontend/src/
    ├── lib/api/studio/
    │   ├── index.ts (updated)
    │   ├── audio.ts
    │   ├── videos.ts
    │   ├── websites.ts
    │   ├── components.ts
    │   ├── ads.ts
    │   ├── emails.ts
    │   └── social-posts.ts
    └── components/studio/
        ├── types.ts (updated)
        ├── index.ts (updated)
        ├── StudioPanel.tsx (updated)
        ├── StudioProgressIndicators.tsx (updated - now 18 types)
        ├── StudioGeneratedContent.tsx (updated - now 18 types)
        ├── StudioModals.tsx (updated - now 17 modals)
        ├── audio/
        │   ├── index.ts
        │   ├── useAudioGeneration.ts
        │   ├── AudioProgressIndicator.tsx
        │   └── AudioListItem.tsx
        ├── video/
        │   ├── index.ts
        │   ├── useVideoGeneration.ts
        │   ├── VideoProgressIndicator.tsx
        │   ├── VideoListItem.tsx
        │   ├── VideoViewer.tsx
        │   └── VideoViewerModal.tsx
        ├── website/
        │   ├── index.ts
        │   ├── useWebsiteGeneration.ts
        │   ├── WebsiteProgressIndicator.tsx
        │   ├── WebsiteListItem.tsx
        │   ├── WebsiteViewer.tsx
        │   └── WebsiteViewerModal.tsx
        ├── components/
        │   ├── index.ts
        │   ├── useComponentGeneration.ts
        │   ├── ComponentProgressIndicator.tsx
        │   ├── ComponentListItem.tsx
        │   ├── ComponentViewer.tsx
        │   └── ComponentViewerModal.tsx
        ├── ads/
        │   ├── index.ts
        │   ├── useAdGeneration.ts
        │   ├── AdProgressIndicator.tsx
        │   ├── AdListItem.tsx
        │   └── AdViewerModal.tsx
        ├── email/
        │   ├── index.ts
        │   ├── useEmailGeneration.ts
        │   ├── EmailProgressIndicator.tsx
        │   ├── EmailListItem.tsx
        │   └── EmailViewerModal.tsx
        └── social/
            ├── index.ts
            ├── useSocialPostGeneration.ts
            ├── SocialPostProgressIndicator.tsx
            ├── SocialPostListItem.tsx
            └── SocialPostViewerModal.tsx
```

## Testing

### Backend Verification
- All Python files pass syntax check (`python -m py_compile`)
- API blueprints registered in studio __init__.py
- Services properly import from KnowBook patterns

### Frontend Verification
- TypeScript compilation passes without errors
- All component exports properly configured
- API types match backend response structures

## Studio Content Types Summary

With Module 10 complete, the Studio panel now supports **18 content generation types** across 4 modules:

| Module | Content Types |
|--------|---------------|
| Module 7 (Documents) | PRD, Blog, Marketing Strategy, Business Report |
| Module 8 (Visual) | Mind Map, Flow Diagram, Infographic, Wireframe |
| Module 9 (Learning) | Quiz, Flash Cards, Presentation |
| Module 10 (Media & Code) | Audio, Video, Website, Component, Ad, Email, Social Posts |

## External Service Requirements

| Feature | Service | API Key Required |
|---------|---------|------------------|
| Audio Overview | ElevenLabs TTS | `ELEVENLABS_API_KEY` |
| Video Generation | Google Veo 2.0 | `GEMINI_API_KEY` |
| Ad Creatives | Gemini Imagen | `GEMINI_API_KEY` |
| Email Images | Gemini Imagen | `GEMINI_API_KEY` |

---

## Module 10 Complete!

Module 10 successfully completes the Studio panel with media and code generation capabilities. This final Studio module brings the total to 18 AI-powered content generation tools, enabling users to transform their source documents into rich, diverse content formats.

**Studio Panel Implementation Complete!**

The full KnowBook Studio now matches NoobBook's complete feature set with:
- 4 Document types (Module 7)
- 4 Visual types (Module 8)
- 3 Interactive Learning types (Module 9)
- 7 Media & Code types (Module 10)

**Ready to merge!**
