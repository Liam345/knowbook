/**
 * Studio Types
 * Educational Note: Centralized type definitions for Studio panel.
 * Studio items are activated by signals from the main chat based on context.
 */

import {
  FileText,
  Brain,
  ChartBar,
  Target,
  Article,
  TreeStructure,
  ChartPieSlice,
  FlowArrow,
  Layout,
  Exam,
  Cards,
  Presentation,
} from '@phosphor-icons/react';

/**
 * Studio item categories - matches backend enum
 */
export type GenerationCategory = 'learning' | 'business' | 'content';

/**
 * Studio item IDs - matches backend studio_item enum exactly
 * Module 7: Document generation types
 * Module 8: Visual content types (mind_map, flow_diagram, infographics, wireframes)
 * Module 9: Interactive content types (quiz, flash_cards, presentation)
 */
export type StudioItemId =
  | 'business_report'
  | 'marketing_strategy'
  | 'prd'
  | 'blog'
  | 'mind_map'
  | 'flow_diagram'
  | 'infographics'
  | 'wireframes'
  | 'quiz'
  | 'flash_cards'
  | 'presentation';

/**
 * Studio signal from backend - sent by main chat AI
 * Educational Note: These signals activate studio items contextually.
 * Multiple signals can exist for the same studio_item (different topics).
 */
export interface StudioSignal {
  id: string;
  studio_item: StudioItemId;
  direction: string;
  sources: Array<{
    source_id: string;
    chunk_ids?: string[];
  }>;
  created_at: string;
}

/**
 * Single generation option configuration
 */
export interface GenerationOption {
  id: StudioItemId;
  title: string;
  description: string;
  icon: React.ComponentType<{ size?: number; className?: string }>;
  category: GenerationCategory;
}

/**
 * All available generation options
 * Educational Note: Organized by category - Learning, Business, Content
 */
export const generationOptions: GenerationOption[] = [
  // BUSINESS
  {
    id: 'business_report',
    title: 'Business Report',
    description: 'Data insights & metrics',
    icon: ChartBar,
    category: 'business',
  },
  {
    id: 'marketing_strategy',
    title: 'Marketing Strategy',
    description: 'Growth plans & positioning',
    icon: Target,
    category: 'business',
  },
  {
    id: 'prd',
    title: 'PRD',
    description: 'Product requirements doc',
    icon: FileText,
    category: 'business',
  },

  // LEARNING (Module 9 - Interactive Content)
  {
    id: 'quiz',
    title: 'Quiz',
    description: 'Test your knowledge',
    icon: Exam,
    category: 'learning',
  },
  {
    id: 'flash_cards',
    title: 'Flash Cards',
    description: 'Study cards from sources',
    icon: Cards,
    category: 'learning',
  },

  // VISUAL (Module 8)
  {
    id: 'mind_map',
    title: 'Mind Map',
    description: 'Visualize relationships',
    icon: TreeStructure,
    category: 'learning',
  },
  {
    id: 'infographics',
    title: 'Infographics',
    description: 'Visual data storytelling',
    icon: ChartPieSlice,
    category: 'business',
  },
  {
    id: 'flow_diagram',
    title: 'Flow Diagram',
    description: 'Process & system flows',
    icon: FlowArrow,
    category: 'business',
  },
  {
    id: 'wireframes',
    title: 'Wireframes',
    description: 'UI/UX design mockups',
    icon: Layout,
    category: 'business',
  },

  // CONTENT
  {
    id: 'blog',
    title: 'Blog Post',
    description: 'Long-form articles',
    icon: Article,
    category: 'content',
  },
  {
    id: 'presentation',
    title: 'Presentation',
    description: 'Slide deck builder',
    icon: Presentation,
    category: 'business',
  },
];

/**
 * Category metadata for section headers
 */
export const categoryMeta: Record<
  GenerationCategory,
  { label: string; icon: React.ComponentType<{ size?: number; className?: string }> }
> = {
  learning: { label: 'Learning', icon: Brain },
  business: { label: 'Business & Product', icon: ChartBar },
  content: { label: 'Content', icon: Article },
};

/**
 * Helper to get signals for a specific studio item
 */
export const getSignalsForItem = (
  signals: StudioSignal[],
  itemId: StudioItemId
): StudioSignal[] => {
  return signals.filter((s) => s.studio_item === itemId);
};

/**
 * Helper to check if a studio item is active (has signals)
 */
export const isItemActive = (
  signals: StudioSignal[],
  itemId: StudioItemId
): boolean => {
  return signals.some((s) => s.studio_item === itemId);
};
