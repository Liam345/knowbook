/**
 * StudioModals Component
 * Educational Note: Renders all studio viewer modals.
 * Consolidates modal components for cleaner StudioPanel structure.
 * Module 7: PRD, Blog, Marketing Strategy, and Business Report.
 * Module 8: Mind Map, Flow Diagram, Infographic, and Wireframe.
 */

import React from 'react';
import { PRDViewerModal } from './prd';
import { MarketingStrategyViewerModal } from './marketingStrategy';
import { BlogViewerModal } from './blog';
import { BusinessReportViewerModal } from './businessReport';
import { MindMapViewerModal } from './mindmap';
import { FlowDiagramViewerModal } from './flow-diagrams';
import { InfographicViewerModal } from './infographic';
import { WireframeViewerModal } from './wireframes';
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

interface StudioModalsProps {
  projectId: string;

  // PRD
  viewingPRDJob: PRDJob | null;
  setViewingPRDJob: (job: PRDJob | null) => void;
  downloadPRD: (jobId: string) => void;

  // Marketing Strategy
  viewingMarketingStrategyJob: MarketingStrategyJob | null;
  setViewingMarketingStrategyJob: (job: MarketingStrategyJob | null) => void;
  downloadMarketingStrategy: (jobId: string) => void;

  // Blog
  viewingBlogJob: BlogJob | null;
  setViewingBlogJob: (job: BlogJob | null) => void;
  downloadBlog: (jobId: string) => void;

  // Business Report
  viewingBusinessReportJob: BusinessReportJob | null;
  setViewingBusinessReportJob: (job: BusinessReportJob | null) => void;
  downloadBusinessReport: (jobId: string) => void;

  // Mind Map (Module 8)
  viewingMindMapJob: MindMapJob | null;
  setViewingMindMapJob: (job: MindMapJob | null) => void;

  // Flow Diagram (Module 8)
  viewingFlowDiagramJob: FlowDiagramJob | null;
  setViewingFlowDiagramJob: (job: FlowDiagramJob | null) => void;

  // Infographic (Module 8)
  viewingInfographicJob: InfographicJob | null;
  setViewingInfographicJob: (job: InfographicJob | null) => void;

  // Wireframe (Module 8)
  viewingWireframeJob: WireframeJob | null;
  setViewingWireframeJob: (job: WireframeJob | null) => void;
}

export const StudioModals: React.FC<StudioModalsProps> = ({
  projectId,
  viewingPRDJob,
  setViewingPRDJob,
  downloadPRD,
  viewingMarketingStrategyJob,
  setViewingMarketingStrategyJob,
  downloadMarketingStrategy,
  viewingBlogJob,
  setViewingBlogJob,
  downloadBlog,
  viewingBusinessReportJob,
  setViewingBusinessReportJob,
  downloadBusinessReport,
  viewingMindMapJob,
  setViewingMindMapJob,
  viewingFlowDiagramJob,
  setViewingFlowDiagramJob,
  viewingInfographicJob,
  setViewingInfographicJob,
  viewingWireframeJob,
  setViewingWireframeJob,
}) => {
  return (
    <>
      {/* PRD Viewer Modal */}
      <PRDViewerModal
        projectId={projectId}
        viewingPRDJob={viewingPRDJob}
        onClose={() => setViewingPRDJob(null)}
        onDownload={downloadPRD}
      />

      {/* Marketing Strategy Viewer Modal */}
      <MarketingStrategyViewerModal
        projectId={projectId}
        viewingMarketingStrategyJob={viewingMarketingStrategyJob}
        onClose={() => setViewingMarketingStrategyJob(null)}
        onDownload={downloadMarketingStrategy}
      />

      {/* Blog Viewer Modal */}
      <BlogViewerModal
        projectId={projectId}
        viewingBlogJob={viewingBlogJob}
        onClose={() => setViewingBlogJob(null)}
        onDownload={downloadBlog}
      />

      {/* Business Report Viewer Modal */}
      <BusinessReportViewerModal
        projectId={projectId}
        viewingBusinessReportJob={viewingBusinessReportJob}
        onClose={() => setViewingBusinessReportJob(null)}
        onDownload={downloadBusinessReport}
      />

      {/* Mind Map Viewer Modal (Module 8) */}
      <MindMapViewerModal
        viewingMindMapJob={viewingMindMapJob}
        onClose={() => setViewingMindMapJob(null)}
      />

      {/* Flow Diagram Viewer Modal (Module 8) */}
      <FlowDiagramViewerModal
        viewingFlowDiagramJob={viewingFlowDiagramJob}
        onClose={() => setViewingFlowDiagramJob(null)}
      />

      {/* Infographic Viewer Modal (Module 8) */}
      <InfographicViewerModal
        projectId={projectId}
        viewingInfographicJob={viewingInfographicJob}
        onClose={() => setViewingInfographicJob(null)}
      />

      {/* Wireframe Viewer Modal (Module 8) */}
      <WireframeViewerModal
        viewingWireframeJob={viewingWireframeJob}
        onClose={() => setViewingWireframeJob(null)}
      />
    </>
  );
};
