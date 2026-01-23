# Module 7: Studio - Document Generation

**Status**: COMPLETE

## Overview

Module 7 implements the Studio panel with AI-powered document generation capabilities. This module enables users to generate professional documents (PRDs, Blogs, Marketing Strategies, Business Reports) from their uploaded sources using specialized AI agents with tool-use patterns.

## Components Implemented

### Backend

#### 1. Studio API Blueprint (`/backend/app/api/studio/`)
- `__init__.py` - Main studio blueprint with sub-blueprint registration
- `prds.py` - PRD generation endpoints
- `blogs.py` - Blog generation endpoints
- `marketing_strategies.py` - Marketing strategy generation endpoints
- `business_reports.py` - Business report generation endpoints

Each endpoint module provides:
- `POST /studio/{type}/start` - Start generation job
- `GET /studio/{type}/{job_id}/status` - Poll job status
- `GET /studio/{type}/{job_id}/preview` - Get markdown preview
- `GET /studio/{type}/{job_id}/download` - Download as file
- `GET /studio/{type}/jobs` - List all jobs

#### 2. AI Agent Services (`/backend/app/services/ai_agents/`)
- `prd_agent_service.py` - PRD document generation agent
  - Generates comprehensive Product Requirements Documents
  - Uses tool-use pattern for section-by-section generation
  - Supports vision analysis for extracting requirements from images

- `blog_agent_service.py` - Blog post generation agent
  - Generates SEO-optimized blog posts
  - Supports multiple blog types: tutorial, listicle, thought_leadership, case_study
  - Includes image generation for featured images

- `marketing_strategy_agent_service.py` - Marketing strategy generation agent
  - Generates comprehensive marketing strategy documents
  - Analyzes target market, competitive landscape, positioning

- `business_report_agent_service.py` - Business report generation agent
  - Generates data-driven business reports
  - Supports multiple report types: executive_summary, financial_report, performance_analysis, etc.
  - Integrates with CSV data for chart generation

#### 3. Tool Executors (`/backend/app/services/tool_executors/`)
- `prd_tool_executor.py` - Executes PRD section writing tools
- `blog_tool_executor.py` - Executes blog content writing tools
- `blog_agent_executor.py` - Executes blog agent tools (image generation, etc.)
- `marketing_strategy_tool_executor.py` - Executes marketing strategy tools
- `business_report_tool_executor.py` - Executes business report tools

#### 4. Tool Definitions (`/backend/app/tools/studio/`)
- PRD tools: `write_prd_section.json`
- Blog tools: `write_blog_section.json`, `generate_blog_image.json`
- Marketing tools: `write_marketing_section.json`
- Business report tools: `write_report_section.json`, `generate_chart.json`

### Frontend

#### 1. API Client Layer (`/frontend/src/lib/api/studio/`)
- `index.ts` - Shared types and re-exports
  - `JobStatus` type: 'pending' | 'processing' | 'ready' | 'error'
  - `checkGeminiStatus()` utility
- `prds.ts` - PRD API client with polling support
- `blogs.ts` - Blog API client with image handling
- `marketingStrategies.ts` - Marketing strategy API client
- `businessReports.ts` - Business report API client with chart support

Each API module provides:
- `startGeneration()` - Initiate document generation
- `getJobStatus()` - Check job status
- `pollJobStatus()` - Poll with callback for progress updates
- `getPreview()` - Fetch markdown content
- `getDownloadUrl()` - Get download URL
- `listJobs()` - List completed jobs

#### 2. Studio Panel Components (`/frontend/src/components/studio/`)

**Core Components:**
- `StudioPanel.tsx` - Main orchestrator component
  - Manages all generation hooks
  - Routes signals to appropriate generators
  - Handles signal picker for multiple signal scenarios

- `StudioHeader.tsx` - Panel header with MagicWand icon
- `StudioToolsList.tsx` - Tools organized by category (Documents)
- `StudioToolItem.tsx` - Individual tool button with active state
- `StudioCollapsedView.tsx` - Collapsed icon bar view
- `StudioSignalPicker.tsx` - Dialog for selecting signals
- `StudioProgressIndicators.tsx` - Active generation progress
- `StudioGeneratedContent.tsx` - List of generated documents
- `StudioModals.tsx` - Container for all viewer modals
- `types.ts` - Type definitions and generation options
- `index.ts` - Barrel exports

**PRD Components (`/frontend/src/components/studio/prd/`):**
- `usePRDGeneration.ts` - PRD generation hook
- `PRDProgressIndicator.tsx` - Progress with amber theme
- `PRDListItem.tsx` - List item showing document title, sections
- `PRDViewerModal.tsx` - Markdown viewer with styled components
- `index.ts` - Barrel exports

**Blog Components (`/frontend/src/components/studio/blog/`):**
- `useBlogGeneration.ts` - Blog generation hook with keyword/type support
- `BlogProgressIndicator.tsx` - Progress with indigo theme
- `BlogListItem.tsx` - List item showing title, word count
- `BlogViewerModal.tsx` - Markdown viewer with image support
- `index.ts` - Barrel exports

**Marketing Strategy Components (`/frontend/src/components/studio/marketingStrategy/`):**
- `useMarketingStrategyGeneration.ts` - Marketing strategy hook
- `MarketingStrategyProgressIndicator.tsx` - Progress with emerald theme
- `MarketingStrategyListItem.tsx` - List item showing document title
- `MarketingStrategyViewerModal.tsx` - Markdown viewer
- `index.ts` - Barrel exports

**Business Report Components (`/frontend/src/components/studio/businessReport/`):**
- `useBusinessReportGeneration.ts` - Business report hook with report type support
- `BusinessReportProgressIndicator.tsx` - Progress with teal theme
- `BusinessReportListItem.tsx` - List item showing title, charts, word count
- `BusinessReportViewerModal.tsx` - Markdown viewer with chart images
- `index.ts` - Barrel exports

#### 3. UI Components Added
- `src/components/ui/tooltip.tsx` - Tooltip component for collapsed view

## API Endpoints

### PRD Endpoints
- `POST /api/v1/studio/prds/start` - Start PRD generation
- `GET /api/v1/studio/prds/<job_id>/status` - Get job status
- `GET /api/v1/studio/prds/<job_id>/preview` - Get markdown preview
- `GET /api/v1/studio/prds/<job_id>/download` - Download PRD file
- `GET /api/v1/studio/prds/jobs` - List PRD jobs

### Blog Endpoints
- `POST /api/v1/studio/blogs/start` - Start blog generation
- `GET /api/v1/studio/blogs/<job_id>/status` - Get job status
- `GET /api/v1/studio/blogs/<job_id>/preview` - Get markdown preview
- `GET /api/v1/studio/blogs/<job_id>/download` - Download blog file
- `GET /api/v1/studio/blogs/jobs` - List blog jobs

### Marketing Strategy Endpoints
- `POST /api/v1/studio/marketing-strategies/start` - Start generation
- `GET /api/v1/studio/marketing-strategies/<job_id>/status` - Get job status
- `GET /api/v1/studio/marketing-strategies/<job_id>/preview` - Get markdown
- `GET /api/v1/studio/marketing-strategies/<job_id>/download` - Download file
- `GET /api/v1/studio/marketing-strategies/jobs` - List jobs

### Business Report Endpoints
- `POST /api/v1/studio/business-reports/start` - Start generation
- `GET /api/v1/studio/business-reports/<job_id>/status` - Get job status
- `GET /api/v1/studio/business-reports/<job_id>/preview` - Get markdown
- `GET /api/v1/studio/business-reports/<job_id>/download` - Download file
- `GET /api/v1/studio/business-reports/jobs` - List jobs

## Dependencies Added

### Frontend (package.json)
- `@radix-ui/react-tooltip` - Tooltip UI primitives
- `react-markdown` - Markdown rendering
- `remark-gfm` - GitHub Flavored Markdown support

## Architecture Notes

### Agent Pattern
```
User triggers generation via StudioPanel
    → Frontend calls POST /studio/{type}/start
    → Backend creates job, spawns background thread
    → Agent runs with tool-use loop:
        → Claude analyzes source content
        → Calls write_section tool for each section
        → Tool executor appends to markdown file
        → Job status updated with progress
    → Frontend polls /status with progress callback
    → On completion, opens ViewerModal with preview
```

### Generation Hook Pattern
```typescript
const {
  savedJobs,           // Completed jobs array
  currentJob,          // In-progress job or null
  isGenerating,        // Boolean loading state
  viewingJob,          // Job being viewed in modal
  setViewingJob,       // Modal visibility control
  loadSavedJobs,       // Load from backend
  handleGeneration,    // Trigger new generation
  download,            // Download file
} = use{Type}Generation(projectId);
```

### Polling Pattern
```
startGeneration() returns job_id
    → pollJobStatus() with onProgress callback
    → Initial interval: 2 seconds
    → After 30s: increase to 5 seconds
    → Continues until status is 'ready' or 'error'
    → Progress callback updates UI state
```

### Color Themes
- PRD: Amber (`amber-500`, `amber-600`)
- Blog: Indigo (`indigo-500`, `indigo-600`)
- Marketing Strategy: Emerald (`emerald-500`, `emerald-600`)
- Business Report: Teal (`teal-500`, `teal-600`)

## File Structure

```
knowbook/
├── backend/app/
│   ├── api/studio/
│   │   ├── __init__.py
│   │   ├── prds.py
│   │   ├── blogs.py
│   │   ├── marketing_strategies.py
│   │   └── business_reports.py
│   ├── services/
│   │   ├── ai_agents/
│   │   │   ├── prd_agent_service.py
│   │   │   ├── blog_agent_service.py
│   │   │   ├── marketing_strategy_agent_service.py
│   │   │   └── business_report_agent_service.py
│   │   └── tool_executors/
│   │       ├── prd_tool_executor.py
│   │       ├── blog_tool_executor.py
│   │       ├── blog_agent_executor.py
│   │       ├── marketing_strategy_tool_executor.py
│   │       └── business_report_tool_executor.py
│   └── tools/studio/
│       └── (tool JSON definitions)
│
└── frontend/src/
    ├── lib/api/
    │   ├── client.ts
    │   └── studio/
    │       ├── index.ts
    │       ├── prds.ts
    │       ├── blogs.ts
    │       ├── marketingStrategies.ts
    │       └── businessReports.ts
    └── components/
        ├── ui/tooltip.tsx
        └── studio/
            ├── StudioPanel.tsx
            ├── StudioHeader.tsx
            ├── StudioToolsList.tsx
            ├── StudioToolItem.tsx
            ├── StudioCollapsedView.tsx
            ├── StudioSignalPicker.tsx
            ├── StudioProgressIndicators.tsx
            ├── StudioGeneratedContent.tsx
            ├── StudioModals.tsx
            ├── types.ts
            ├── index.ts
            ├── prd/
            │   ├── usePRDGeneration.ts
            │   ├── PRDProgressIndicator.tsx
            │   ├── PRDListItem.tsx
            │   ├── PRDViewerModal.tsx
            │   └── index.ts
            ├── blog/
            │   ├── useBlogGeneration.ts
            │   ├── BlogProgressIndicator.tsx
            │   ├── BlogListItem.tsx
            │   ├── BlogViewerModal.tsx
            │   └── index.ts
            ├── marketingStrategy/
            │   ├── useMarketingStrategyGeneration.ts
            │   ├── MarketingStrategyProgressIndicator.tsx
            │   ├── MarketingStrategyListItem.tsx
            │   ├── MarketingStrategyViewerModal.tsx
            │   └── index.ts
            └── businessReport/
                ├── useBusinessReportGeneration.ts
                ├── BusinessReportProgressIndicator.tsx
                ├── BusinessReportListItem.tsx
                ├── BusinessReportViewerModal.tsx
                └── index.ts
```

## Testing

- All frontend components created (30 files)
- All backend services implemented (4 agents, 5 executors)
- API blueprint registered in main app
- Dependencies added to package.json

## Next Steps (Module 8+)

- Audio overview generation (podcast-style summaries)
- Video overview generation
- Mind map generation
- Presentation generation
- Flash card generation
- Quiz generation
