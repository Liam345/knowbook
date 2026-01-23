/**
 * StudioModals Component
 * Educational Note: Renders all studio viewer modals.
 * Consolidates modal components for cleaner StudioPanel structure.
 * Module 7: Only includes PRD, Blog, Marketing Strategy, and Business Report.
 */

import React from 'react';
import { PRDViewerModal } from './prd';
import { MarketingStrategyViewerModal } from './marketingStrategy';
import { BlogViewerModal } from './blog';
import { BusinessReportViewerModal } from './businessReport';
import type {
  PRDJob,
  MarketingStrategyJob,
  BlogJob,
  BusinessReportJob
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
    </>
  );
};
