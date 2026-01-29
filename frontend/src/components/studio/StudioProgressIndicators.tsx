/**
 * StudioProgressIndicators Component
 * Educational Note: Shows progress for all active studio generation jobs.
 * Consolidates all progress indicators in one place.
 * Module 7: PRD, Blog, Marketing Strategy, and Business Report.
 * Module 8: Mind Map, Flow Diagram, Infographic, and Wireframe.
 */

import React from 'react';
import { PRDProgressIndicator } from './prd';
import { MarketingStrategyProgressIndicator } from './marketingStrategy';
import { BlogProgressIndicator } from './blog';
import { BusinessReportProgressIndicator } from './businessReport';
import { MindMapProgressIndicator } from './mindmap';
import { FlowDiagramProgressIndicator } from './flow-diagrams';
import { InfographicProgressIndicator } from './infographic';
import { WireframeProgressIndicator } from './wireframes';
import type {
  PRDJob,
  MarketingStrategyJob,
  BlogJob,
  BusinessReportJob,
  MindMapJob,
  FlowDiagramJob,
  InfographicJob,
  WireframeJob,
} from '@/lib/api/studio';

interface StudioProgressIndicatorsProps {
  // PRD
  isGeneratingPRD: boolean;
  currentPRDJob: PRDJob | null;

  // Marketing Strategy
  isGeneratingMarketingStrategy: boolean;
  currentMarketingStrategyJob: MarketingStrategyJob | null;

  // Blog
  isGeneratingBlog: boolean;
  currentBlogJob: BlogJob | null;

  // Business Report
  isGeneratingBusinessReport: boolean;
  currentBusinessReportJob: BusinessReportJob | null;

  // Mind Map (Module 8)
  isGeneratingMindMap: boolean;
  currentMindMapJob: MindMapJob | null;

  // Flow Diagram (Module 8)
  isGeneratingFlowDiagram: boolean;
  currentFlowDiagramJob: FlowDiagramJob | null;

  // Infographic (Module 8)
  isGeneratingInfographic: boolean;
  currentInfographicJob: InfographicJob | null;

  // Wireframe (Module 8)
  isGeneratingWireframe: boolean;
  currentWireframeJob: WireframeJob | null;
}

export const StudioProgressIndicators: React.FC<StudioProgressIndicatorsProps> = ({
  isGeneratingPRD,
  currentPRDJob,
  isGeneratingMarketingStrategy,
  currentMarketingStrategyJob,
  isGeneratingBlog,
  currentBlogJob,
  isGeneratingBusinessReport,
  currentBusinessReportJob,
  isGeneratingMindMap,
  currentMindMapJob,
  isGeneratingFlowDiagram,
  currentFlowDiagramJob,
  isGeneratingInfographic,
  currentInfographicJob,
  isGeneratingWireframe,
  currentWireframeJob,
}) => {
  return (
    <>
      {/* PRD Generation Progress */}
      {isGeneratingPRD && (
        <PRDProgressIndicator currentPRDJob={currentPRDJob} />
      )}

      {/* Marketing Strategy Generation Progress */}
      {isGeneratingMarketingStrategy && (
        <MarketingStrategyProgressIndicator currentMarketingStrategyJob={currentMarketingStrategyJob} />
      )}

      {/* Blog Generation Progress */}
      {isGeneratingBlog && (
        <BlogProgressIndicator currentBlogJob={currentBlogJob} />
      )}

      {/* Business Report Generation Progress */}
      {isGeneratingBusinessReport && (
        <BusinessReportProgressIndicator currentBusinessReportJob={currentBusinessReportJob} />
      )}

      {/* Mind Map Generation Progress (Module 8) */}
      {isGeneratingMindMap && (
        <MindMapProgressIndicator currentMindMapJob={currentMindMapJob} />
      )}

      {/* Flow Diagram Generation Progress (Module 8) */}
      {isGeneratingFlowDiagram && (
        <FlowDiagramProgressIndicator currentFlowDiagramJob={currentFlowDiagramJob} />
      )}

      {/* Infographic Generation Progress (Module 8) */}
      {isGeneratingInfographic && (
        <InfographicProgressIndicator currentInfographicJob={currentInfographicJob} />
      )}

      {/* Wireframe Generation Progress (Module 8) */}
      {isGeneratingWireframe && (
        <WireframeProgressIndicator currentWireframeJob={currentWireframeJob} />
      )}
    </>
  );
};
