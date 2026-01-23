/**
 * StudioProgressIndicators Component
 * Educational Note: Shows progress for all active studio generation jobs.
 * Consolidates all progress indicators in one place.
 * Module 7: Only includes PRD, Blog, Marketing Strategy, and Business Report.
 */

import React from 'react';
import { PRDProgressIndicator } from './prd';
import { MarketingStrategyProgressIndicator } from './marketingStrategy';
import { BlogProgressIndicator } from './blog';
import { BusinessReportProgressIndicator } from './businessReport';
import type { PRDJob, MarketingStrategyJob, BlogJob, BusinessReportJob } from '@/lib/api/studio';

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
    </>
  );
};
