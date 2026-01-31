"""
Studio Blueprint - Content generation features from sources.

Educational Note: Studio features generate various content types from source
materials using AI. Each feature follows the same async pattern:

Background Job Pattern:
1. POST creates job record with status="pending"
2. Submits task to ThreadPoolExecutor via task_service
3. Returns job_id immediately (202 Accepted)
4. Frontend polls GET /jobs/{job_id} for status
5. When status="ready", content URL is available

This pattern is essential for long-running AI operations:
- Document generation can take 30+ seconds (multiple AI calls)
- User gets immediate feedback, not blocked UI

Content Types Generated:
- Blog Post: SEO-optimized blog posts with images (Claude + Gemini)
- PRD: Product Requirements Documents in Markdown (Claude)
- Marketing Strategy: Marketing strategy documents in Markdown (Claude)
- Business Report: Business reports with data analysis (Claude)
- Mind Map: Hierarchical concept maps for visual learning (Claude)
- Flow Diagram: Mermaid.js diagrams for processes/workflows (Claude)
- Infographic: Visual infographics (Claude + Gemini Imagen)
- Wireframe: UI/UX wireframes in Excalidraw format (Claude)
- Quiz: Multiple choice questions for knowledge testing (Claude)
- Flash Cards: Study cards with front/back pairs (Claude)
- Presentation: PowerPoint slides exported as PPTX (Claude + Playwright)
- Audio Overview: TTS-based audio summaries (Claude + ElevenLabs)
- Video: AI-generated video clips (Claude + Google Veo)
- Website: Multi-page websites with HTML/CSS/JS (Claude + Gemini)
- Components: Reusable UI components (Claude)
- Ad Creative: Marketing images for ads (Claude + Gemini Imagen)
- Email Template: HTML email templates (Claude + Gemini)
- Social Posts: Platform-specific social media content (Claude + Gemini)

Routes:
- POST /projects/<id>/studio/<type>           - Start generation
- GET  /projects/<id>/studio/<type>-jobs      - List jobs
- GET  /projects/<id>/studio/<type>-jobs/<id> - Job status
- GET  /projects/<id>/studio/<type>/<file>    - Serve generated files
"""
from flask import Blueprint

# Create the studio blueprint
studio_bp = Blueprint('studio', __name__)

# Import route modules to register them with the blueprint
from app.api.studio import prds  # noqa: F401
from app.api.studio import blogs  # noqa: F401
from app.api.studio import marketing_strategies  # noqa: F401
from app.api.studio import business_reports  # noqa: F401
from app.api.studio import mind_maps  # noqa: F401
from app.api.studio import flow_diagrams  # noqa: F401
from app.api.studio import infographics  # noqa: F401
from app.api.studio import wireframes  # noqa: F401
from app.api.studio import quizzes  # noqa: F401
from app.api.studio import flash_cards  # noqa: F401
from app.api.studio import presentations  # noqa: F401
from app.api.studio import audio  # noqa: F401
from app.api.studio import videos  # noqa: F401
from app.api.studio import websites  # noqa: F401
from app.api.studio import components  # noqa: F401
from app.api.studio import ads  # noqa: F401
from app.api.studio import emails  # noqa: F401
from app.api.studio import social_posts  # noqa: F401

# Educational Note: The noqa comments tell flake8 to ignore the
# "imported but unused" warning. We import to register routes,
# not to use the module directly.
