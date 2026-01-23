/**
 * StudioGeneratedContent Component
 * Educational Note: Displays all generated studio content items.
 * Shows list items for each completed job, filtered by active signals.
 * Module 7: Only includes PRD, Blog, Marketing Strategy, and Business Report.
 */

import React from 'react';
import { MagicWand } from '@phosphor-icons/react';
import { PRDListItem } from './prd';
import { MarketingStrategyListItem } from './marketingStrategy';
import { BlogListItem } from './blog';
import { BusinessReportListItem } from './businessReport';
import type {
  PRDJob,
  MarketingStrategyJob,
  BlogJob,
  BusinessReportJob
} from '@/lib/api/studio';
import type { StudioSignal } from './types';

interface StudioGeneratedContentProps {
  signals: StudioSignal[];

  // PRD
  savedPRDJobs: PRDJob[];
  setViewingPRDJob: (job: PRDJob) => void;
  downloadPRD: (jobId: string) => void;

  // Marketing Strategy
  savedMarketingStrategyJobs: MarketingStrategyJob[];
  setViewingMarketingStrategyJob: (job: MarketingStrategyJob) => void;
  downloadMarketingStrategy: (jobId: string) => void;

  // Blog
  savedBlogJobs: BlogJob[];
  setViewingBlogJob: (job: BlogJob) => void;
  downloadBlog: (jobId: string) => void;

  // Business Report
  savedBusinessReportJobs: BusinessReportJob[];
  setViewingBusinessReportJob: (job: BusinessReportJob) => void;
  downloadBusinessReport: (jobId: string) => void;
}

export const StudioGeneratedContent: React.FC<StudioGeneratedContentProps> = ({
  signals,
  savedPRDJobs,
  setViewingPRDJob,
  downloadPRD,
  savedMarketingStrategyJobs,
  setViewingMarketingStrategyJob,
  downloadMarketingStrategy,
  savedBlogJobs,
  setViewingBlogJob,
  downloadBlog,
  savedBusinessReportJobs,
  setViewingBusinessReportJob,
  downloadBusinessReport,
}) => {
  if (signals.length === 0) {
    return (
      <div className="text-center py-6 text-muted-foreground">
        <MagicWand size={20} className="mx-auto mb-1.5 opacity-50" />
        <p className="text-[10px]">Select a chat to see content</p>
      </div>
    );
  }

  return (
    <>
      {/* Saved PRD Jobs - filter by source_id from signals */}
      {savedPRDJobs
        .filter((job) =>
          signals.some((s) => s.sources.some((src) => src.source_id === job.source_id))
        )
        .map((job) => (
          <PRDListItem
            key={job.id}
            job={job}
            onOpen={() => setViewingPRDJob(job)}
            onDownload={(e) => {
              e.stopPropagation();
              downloadPRD(job.id);
            }}
          />
        ))}

      {/* Saved Marketing Strategy Jobs - filter by source_id from signals */}
      {savedMarketingStrategyJobs
        .filter((job) =>
          signals.some((s) => s.sources.some((src) => src.source_id === job.source_id))
        )
        .map((job) => (
          <MarketingStrategyListItem
            key={job.id}
            job={job}
            onOpen={() => setViewingMarketingStrategyJob(job)}
            onDownload={(e) => {
              e.stopPropagation();
              downloadMarketingStrategy(job.id);
            }}
          />
        ))}

      {/* Saved Blog Jobs - filter by source_id from signals */}
      {savedBlogJobs
        .filter((job) =>
          signals.some((s) => s.sources.some((src) => src.source_id === job.source_id))
        )
        .map((job) => (
          <BlogListItem
            key={job.id}
            job={job}
            onOpen={() => setViewingBlogJob(job)}
            onDownload={(e) => {
              e.stopPropagation();
              downloadBlog(job.id);
            }}
          />
        ))}

      {/* Saved Business Report Jobs - filter by source_id from signals */}
      {savedBusinessReportJobs
        .filter((job) =>
          signals.some((s) => s.sources.some((src) => src.source_id === job.source_id))
        )
        .map((job) => (
          <BusinessReportListItem
            key={job.id}
            job={job}
            onOpen={() => setViewingBusinessReportJob(job)}
            onDownload={(e) => {
              e.stopPropagation();
              downloadBusinessReport(job.id);
            }}
          />
        ))}
    </>
  );
};
