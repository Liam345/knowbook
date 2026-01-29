# Module 8: Studio - Visual Content

**Status**: COMPLETE

## Overview

Module 8 extends the Studio panel with AI-powered visual content generation capabilities. This module enables users to generate visual representations of their sources including Mind Maps, Flow Diagrams, Infographics, and Wireframes. Each visual type uses specialized AI prompts and rendering libraries for optimal output.

## Components Implemented

### Backend

#### 1. Studio API Endpoints (`/backend/app/api/studio/`)
- `mind_maps.py` - Mind map generation endpoints
- `flow_diagrams.py` - Flow diagram generation endpoints
- `infographics.py` - Infographic generation endpoints
- `wireframes.py` - Wireframe generation endpoints

Each endpoint module provides:
- `POST /studio/{type}` - Start generation job
- `GET /studio/{type}-jobs/{job_id}` - Poll job status
- `GET /studio/{type}-jobs` - List all jobs
- `GET /studio/infographics/{filename}` - Serve infographic images (infographics only)

#### 2. Studio Services (`/backend/app/services/studio_services/`)
- `mind_map_service.py` - Mind map generation service
  - Generates hierarchical node structures for visualization
  - Uses Claude to extract concepts and relationships from source content
  - Returns nodes with parent_id relationships for tree rendering

- `flow_diagram_service.py` - Flow diagram generation service
  - Generates Mermaid.js syntax for various diagram types
  - Supports: flowchart, sequence, state, ER, class, pie, gantt, journey
  - Claude analyzes content and selects appropriate diagram type

- `infographic_service.py` - Infographic generation service
  - Two-step AI generation: Claude for prompt generation → Gemini for image
  - Extracts key sections and visual descriptions
  - Generates actual images using Gemini Imagen API

- `wireframe_service.py` - Wireframe generation service
  - Generates Excalidraw-compatible element definitions
  - Creates hand-drawn style UI mockups
  - Uses excalidraw_utils for element conversion

#### 3. Job Management (`/backend/app/services/studio_services/jobs/`)
- `mind_map_jobs.py` - CRUD operations for mind map jobs
- `flow_diagram_jobs.py` - CRUD operations for flow diagram jobs
- `infographic_jobs.py` - CRUD operations for infographic jobs
- `wireframe_jobs.py` - CRUD operations for wireframe jobs

#### 4. Tool Definitions (`/backend/app/services/tools/studio_tools/`)
- `mind_map_tool.json` - Mind map node submission tool
- `flow_diagram_tool.json` - Mermaid syntax submission tool
- `infographic_tool.json` - Infographic content extraction tool
- `wireframe_tool.json` - Wireframe element submission tool

#### 5. Prompt Configurations (`/backend/data/prompts/`)
- `mind_map_prompt.json` - System prompt for mind map generation
- `flow_diagram_prompt.json` - System prompt for flow diagram generation
- `infographic_prompt.json` - System prompt for infographic generation
- `wireframe_prompt.json` - System prompt for wireframe generation

#### 6. Utilities (`/backend/app/utils/`)
- `excalidraw_utils.py` - Converts Claude wireframe output to Excalidraw element format

### Frontend

#### 1. API Client Layer (`/frontend/src/lib/api/studio/`)
- `mind-maps.ts` - Mind map API client with types and polling
  - `MindMapNode` interface with id, label, parent_id, node_type
  - `MindMapJob` interface with nodes array and topic_summary

- `flow-diagrams.ts` - Flow diagram API client
  - `DiagramType` union type for Mermaid diagram types
  - `FlowDiagramJob` interface with mermaid_syntax and diagram_type

- `infographics.ts` - Infographic API client
  - `InfographicImage` and `InfographicKeySection` interfaces
  - `InfographicJob` interface with image_url and key_sections
  - `getImageUrl()` helper for image serving

- `wireframes.ts` - Wireframe API client
  - `ExcalidrawElement` interface matching Excalidraw schema
  - `WireframeJob` interface with elements array and canvas dimensions

Updated `index.ts` to re-export all new APIs and types.

#### 2. Mind Map Components (`/frontend/src/components/studio/mindmap/`)
- `useMindMapGeneration.ts` - Generation hook with state management
- `MindMapProgressIndicator.tsx` - Progress with blue theme
- `MindMapListItem.tsx` - List item showing source name and node count
- `MindMapViewer.tsx` - Interactive React Flow visualization
  - Horizontal tree layout using dagre library
  - Collapsible nodes (start collapsed, click to expand)
  - Custom node styling by type (root/category/leaf)
  - Pan, zoom controls and toolbar
  - Expand/collapse all functionality
- `MindMapViewerModal.tsx` - Modal wrapper for viewer
- `mindMapLayout.ts` - Dagre layout calculation utilities
- `index.ts` - Barrel exports

#### 3. Flow Diagram Components (`/frontend/src/components/studio/flow-diagrams/`)
- `useFlowDiagramGeneration.ts` - Generation hook
- `FlowDiagramProgressIndicator.tsx` - Progress with purple theme
- `FlowDiagramListItem.tsx` - List item showing diagram type
- `FlowDiagramViewer.tsx` - Mermaid.js renderer
  - Pan and zoom support
  - Fullscreen toggle
  - SVG download capability
- `FlowDiagramViewerModal.tsx` - Modal wrapper
- `index.ts` - Barrel exports

#### 4. Infographic Components (`/frontend/src/components/studio/infographic/`)
- `useInfographicGeneration.ts` - Generation hook with Gemini status check
- `InfographicProgressIndicator.tsx` - Progress with pink theme
- `InfographicListItem.tsx` - List item showing topic title
- `InfographicViewerModal.tsx` - Image viewer with download
- `index.ts` - Barrel exports

#### 5. Wireframe Components (`/frontend/src/components/studio/wireframes/`)
- `useWireframeGeneration.ts` - Generation hook
- `WireframeProgressIndicator.tsx` - Progress with slate theme
- `WireframeListItem.tsx` - List item showing element count
- `WireframeViewer.tsx` - Excalidraw renderer
  - Read-only Excalidraw component
  - Hand-drawn aesthetic
  - Pan and zoom support
- `WireframeViewerModal.tsx` - Modal wrapper
- `index.ts` - Barrel exports

#### 6. Updated Core Components
- `types.ts` - Added mind_map, flow_diagram, infographics, wireframes to StudioItemId
  - Added generationOptions entries with icons
- `index.ts` - Added exports for all new component directories
- `StudioPanel.tsx` - Integrated all 4 new generation hooks
- `StudioProgressIndicators.tsx` - Added all 4 progress indicators
- `StudioGeneratedContent.tsx` - Added all 4 list item renderers
- `StudioModals.tsx` - Added all 4 viewer modals

## API Endpoints

### Mind Map Endpoints
- `POST /api/v1/projects/{project_id}/studio/mind-map` - Start generation
- `GET /api/v1/projects/{project_id}/studio/mind-map-jobs/{job_id}` - Get job status
- `GET /api/v1/projects/{project_id}/studio/mind-map-jobs` - List jobs

### Flow Diagram Endpoints
- `POST /api/v1/projects/{project_id}/studio/flow-diagram` - Start generation
- `GET /api/v1/projects/{project_id}/studio/flow-diagram-jobs/{job_id}` - Get job status
- `GET /api/v1/projects/{project_id}/studio/flow-diagram-jobs` - List jobs

### Infographic Endpoints
- `POST /api/v1/projects/{project_id}/studio/infographic` - Start generation
- `GET /api/v1/projects/{project_id}/studio/infographic-jobs/{job_id}` - Get job status
- `GET /api/v1/projects/{project_id}/studio/infographic-jobs` - List jobs
- `GET /api/v1/projects/{project_id}/studio/infographics/{filename}` - Serve image

### Wireframe Endpoints
- `POST /api/v1/projects/{project_id}/studio/wireframe` - Start generation
- `GET /api/v1/projects/{project_id}/studio/wireframe-jobs/{job_id}` - Get job status
- `GET /api/v1/projects/{project_id}/studio/wireframe-jobs` - List jobs

## Data Models

### Mind Map Node
```typescript
interface MindMapNode {
  id: string;
  label: string;
  parent_id: string | null;  // null for root
  node_type: 'root' | 'category' | 'leaf';
  description: string;
}
```

### Flow Diagram Job
```typescript
interface FlowDiagramJob {
  id: string;
  mermaid_syntax: string | null;
  diagram_type: 'flowchart' | 'sequence' | 'state' | 'er' | 'class' | 'pie' | 'gantt' | 'journey' | 'mindmap';
  title: string | null;
  description: string | null;
  // ... common job fields
}
```

### Infographic Job
```typescript
interface InfographicJob {
  id: string;
  topic_title: string | null;
  topic_summary: string | null;
  key_sections: InfographicKeySection[];
  image: InfographicImage | null;
  image_url: string | null;
  image_prompt: string | null;
  // ... common job fields
}
```

### Wireframe Job
```typescript
interface WireframeJob {
  id: string;
  title: string | null;
  description: string | null;
  elements: ExcalidrawElement[];
  canvas_width: number;
  canvas_height: number;
  element_count: number;
  // ... common job fields
}
```

## Dependencies

### Frontend (package.json)
- `@xyflow/react` - React Flow for mind map visualization
- `dagre` - Graph layout algorithm for hierarchical trees
- `mermaid` - Diagram rendering library
- `@excalidraw/excalidraw` - Hand-drawn style wireframe rendering

### Backend (requirements.txt)
- Existing Claude API for content analysis
- Gemini API for infographic image generation

## Architecture Notes

### Mind Map Generation Pattern
```
User triggers Mind Map generation
    → POST /studio/mind-map with source_id
    → Backend loads source content
    → Claude analyzes and extracts concepts
    → Returns hierarchical nodes (root → categories → leaves)
    → Frontend renders using React Flow + dagre layout
    → User can expand/collapse nodes interactively
```

### Flow Diagram Generation Pattern
```
User triggers Flow Diagram generation
    → POST /studio/flow-diagram with source_id
    → Backend loads source content
    → Claude analyzes and determines best diagram type
    → Returns Mermaid.js syntax
    → Frontend renders using mermaid library
    → User can pan, zoom, fullscreen, and download SVG
```

### Infographic Generation Pattern
```
User triggers Infographic generation
    → Check Gemini API status first
    → POST /studio/infographic with source_id
    → Claude extracts topic, summary, key sections
    → Claude generates optimized image prompt
    → Gemini Imagen generates actual image
    → Image saved to project storage
    → Frontend displays image with download option
```

### Wireframe Generation Pattern
```
User triggers Wireframe generation
    → POST /studio/wireframe with source_id
    → Claude analyzes content for UI requirements
    → Returns element definitions in Excalidraw format
    → excalidraw_utils converts to proper schema
    → Frontend renders using Excalidraw component
    → Read-only view with hand-drawn aesthetic
```

### Color Themes
- Mind Map: Blue (`blue-500`, `blue-600`)
- Flow Diagram: Purple (`purple-500`, `purple-600`)
- Infographic: Pink (`pink-500`, `pink-600`)
- Wireframe: Slate (`slate-500`, `slate-600`)

## File Structure

```
knowbook/
├── backend/app/
│   ├── api/studio/
│   │   ├── __init__.py (updated)
│   │   ├── mind_maps.py
│   │   ├── flow_diagrams.py
│   │   ├── infographics.py
│   │   └── wireframes.py
│   ├── services/studio_services/
│   │   ├── __init__.py
│   │   ├── studio_index_service.py (updated)
│   │   ├── mind_map_service.py
│   │   ├── flow_diagram_service.py
│   │   ├── infographic_service.py
│   │   ├── wireframe_service.py
│   │   └── jobs/
│   │       ├── mind_map_jobs.py
│   │       ├── flow_diagram_jobs.py
│   │       ├── infographic_jobs.py
│   │       └── wireframe_jobs.py
│   ├── services/tools/studio_tools/
│   │   ├── mind_map_tool.json
│   │   ├── flow_diagram_tool.json
│   │   ├── infographic_tool.json
│   │   └── wireframe_tool.json
│   └── utils/
│       └── excalidraw_utils.py
│
├── backend/data/prompts/
│   ├── mind_map_prompt.json
│   ├── flow_diagram_prompt.json
│   ├── infographic_prompt.json
│   └── wireframe_prompt.json
│
└── frontend/src/
    ├── lib/api/studio/
    │   ├── index.ts (updated)
    │   ├── mind-maps.ts
    │   ├── flow-diagrams.ts
    │   ├── infographics.ts
    │   └── wireframes.ts
    └── components/studio/
        ├── types.ts (updated)
        ├── index.ts (updated)
        ├── StudioPanel.tsx (updated)
        ├── StudioProgressIndicators.tsx (updated)
        ├── StudioGeneratedContent.tsx (updated)
        ├── StudioModals.tsx (updated)
        ├── mindmap/
        │   ├── index.ts
        │   ├── useMindMapGeneration.ts
        │   ├── MindMapProgressIndicator.tsx
        │   ├── MindMapListItem.tsx
        │   ├── MindMapViewer.tsx
        │   ├── MindMapViewerModal.tsx
        │   └── mindMapLayout.ts
        ├── flow-diagrams/
        │   ├── index.ts
        │   ├── useFlowDiagramGeneration.ts
        │   ├── FlowDiagramProgressIndicator.tsx
        │   ├── FlowDiagramListItem.tsx
        │   ├── FlowDiagramViewer.tsx
        │   └── FlowDiagramViewerModal.tsx
        ├── infographic/
        │   ├── index.ts
        │   ├── useInfographicGeneration.ts
        │   ├── InfographicProgressIndicator.tsx
        │   ├── InfographicListItem.tsx
        │   └── InfographicViewerModal.tsx
        └── wireframes/
            ├── index.ts
            ├── useWireframeGeneration.ts
            ├── WireframeProgressIndicator.tsx
            ├── WireframeListItem.tsx
            ├── WireframeViewer.tsx
            └── WireframeViewerModal.tsx
```

## Testing

### Backend Verification
- All Python files pass syntax check (`python -m py_compile`)
- API blueprints registered in studio __init__.py
- Services properly import from KnowBook patterns (not NoobBook)

### Frontend Verification
- TypeScript compilation passes without errors
- All component exports properly configured
- API types match backend response structures

## Rendering Libraries

| Visual Type | Library | Features |
|-------------|---------|----------|
| Mind Map | React Flow + dagre | Collapsible nodes, pan/zoom, custom styling |
| Flow Diagram | Mermaid.js | Multiple diagram types, SVG export, fullscreen |
| Infographic | Gemini Imagen | AI-generated images, download support |
| Wireframe | Excalidraw | Hand-drawn aesthetic, read-only view |

## Next Steps (Module 9+)

- Audio overview generation (podcast-style summaries)
- Video overview generation
- Quiz generation
- Flash card generation
- Presentation generation
- Email template generation

---

## Module 8 Complete!

Module 8 successfully adds visual content generation to the Studio panel, providing users with four powerful visualization tools for their source content. Each visual type uses specialized AI prompts and dedicated rendering libraries for optimal output quality.

**Ready to merge and move to Module 9!**
