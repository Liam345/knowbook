/**
 * StudioPanel Component
 * Educational Note: Main orchestrator for the Studio panel.
 * Receives signals from chat and handles generation workflows.
 * Shows a picker when multiple signals exist for the same studio item.
 * Module 7: Only includes PRD, Blog, Marketing Strategy, and Business Report.
 */

import React, { useState, useEffect } from 'react';
import { StudioHeader } from './StudioHeader';
import { StudioToolsList } from './StudioToolsList';
import { generationOptions, type StudioSignal, type StudioItemId } from './types';
import { ScrollArea } from '../ui/scroll-area';
import { useToast } from '../ui/toast';
import { usePRDGeneration } from './prd';
import { useMarketingStrategyGeneration } from './marketingStrategy';
import { useBlogGeneration } from './blog';
import { useBusinessReportGeneration } from './businessReport';
import { StudioCollapsedView } from './StudioCollapsedView';
import { StudioSignalPicker } from './StudioSignalPicker';
import { StudioProgressIndicators } from './StudioProgressIndicators';
import { StudioGeneratedContent } from './StudioGeneratedContent';
import { StudioModals } from './StudioModals';

interface StudioPanelProps {
  projectId: string;
  signals: StudioSignal[];
  isCollapsed?: boolean;
  onExpand?: () => void;
}

export const StudioPanel: React.FC<StudioPanelProps> = ({
  projectId,
  signals,
  isCollapsed,
  onExpand,
}) => {
  const { success: showSuccess } = useToast();

  // State for signal picker dialog
  const [pickerOpen, setPickerOpen] = useState(false);
  const [selectedItem, setSelectedItem] = useState<StudioItemId | null>(null);
  const [selectedSignals, setSelectedSignals] = useState<StudioSignal[]>([]);

  // PRD generation hook
  const {
    savedPRDJobs,
    currentPRDJob,
    isGeneratingPRD,
    viewingPRDJob,
    setViewingPRDJob,
    loadSavedJobs: loadSavedPRDJobs,
    handlePRDGeneration,
    downloadPRD,
  } = usePRDGeneration(projectId);

  // Marketing Strategy generation hook
  const {
    savedMarketingStrategyJobs,
    currentMarketingStrategyJob,
    isGeneratingMarketingStrategy,
    viewingMarketingStrategyJob,
    setViewingMarketingStrategyJob,
    loadSavedJobs: loadSavedMarketingStrategyJobs,
    handleMarketingStrategyGeneration,
    downloadMarketingStrategy,
  } = useMarketingStrategyGeneration(projectId);

  // Blog generation hook
  const {
    savedBlogJobs,
    currentBlogJob,
    isGeneratingBlog,
    viewingBlogJob,
    setViewingBlogJob,
    loadSavedJobs: loadSavedBlogJobs,
    handleBlogGeneration,
    downloadBlog,
  } = useBlogGeneration(projectId);

  // Business Report generation hook
  const {
    savedBusinessReportJobs,
    currentBusinessReportJob,
    isGeneratingBusinessReport,
    viewingBusinessReportJob,
    setViewingBusinessReportJob,
    loadSavedJobs: loadSavedBusinessReportJobs,
    handleBusinessReportGeneration,
    downloadBusinessReport,
  } = useBusinessReportGeneration(projectId);

  // Load saved jobs on mount
  useEffect(() => {
    const loadSavedJobs = async () => {
      try {
        // Load saved PRD jobs
        await loadSavedPRDJobs();

        // Load saved marketing strategy jobs
        await loadSavedMarketingStrategyJobs();

        // Load saved blog jobs
        await loadSavedBlogJobs();

        // Load saved business report jobs
        await loadSavedBusinessReportJobs();

      } catch (error) {
        console.error('Failed to load saved jobs:', error);
      }
    };
    loadSavedJobs();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [projectId]);

  /**
   * Handle generation request
   * Educational Note: If multiple signals exist for an item, show picker.
   * If only one signal, trigger generation directly.
   */
  const handleGenerate = (optionId: StudioItemId, itemSignals: StudioSignal[]) => {
    if (itemSignals.length === 0) return;

    if (itemSignals.length === 1) {
      // Single signal - generate directly
      triggerGeneration(optionId, itemSignals[0]);
    } else {
      // Multiple signals - show picker
      setSelectedItem(optionId);
      setSelectedSignals(itemSignals);
      setPickerOpen(true);
    }
  };

  /**
   * Trigger the actual generation workflow
   * Educational Note: This calls the backend studio generator
   */
  const triggerGeneration = async (optionId: StudioItemId, signal: StudioSignal) => {
    setPickerOpen(false);

    if (optionId === 'prd') {
      await handlePRDGeneration(signal);
    } else if (optionId === 'marketing_strategy') {
      await handleMarketingStrategyGeneration(signal);
    } else if (optionId === 'blog') {
      await handleBlogGeneration(signal);
    } else if (optionId === 'business_report') {
      await handleBusinessReportGeneration(signal);
    } else {
      showSuccess(`${getItemTitle(optionId)} generation is coming soon!`);
    }
  };

  /**
   * Get display name for a studio item
   */
  const getItemTitle = (itemId: StudioItemId): string => {
    const option = generationOptions.find((opt) => opt.id === itemId);
    return option?.title || itemId;
  };

  /**
   * Get icon for a studio item
   */
  const getItemIcon = (itemId: StudioItemId) => {
    const option = generationOptions.find((opt) => opt.id === itemId);
    return option?.icon;
  };

  // Collapsed view - show icon bar with action icons
  if (isCollapsed) {
    return (
      <StudioCollapsedView
        signals={signals}
        onExpand={onExpand!}
        onGenerate={handleGenerate}
      />
    );
  }

  return (
    <div className="flex flex-col h-full">
      <StudioHeader />

      {/* TOP HALF: Generation Tools */}
      <div className="flex-1 min-h-0 border-b flex flex-col">
        <StudioToolsList signals={signals} onGenerate={handleGenerate} />
      </div>

      {/* BOTTOM HALF: Generated Outputs */}
      <div className="flex-1 min-h-0 flex flex-col">
        <div className="px-3 py-2 border-b">
          <h3 className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
            Generated Content
          </h3>
        </div>

        <ScrollArea className="flex-1">
          <div className="p-3 space-y-2">
            {/* Progress Indicators */}
            <StudioProgressIndicators
              isGeneratingPRD={isGeneratingPRD}
              currentPRDJob={currentPRDJob}
              isGeneratingMarketingStrategy={isGeneratingMarketingStrategy}
              currentMarketingStrategyJob={currentMarketingStrategyJob}
              isGeneratingBlog={isGeneratingBlog}
              currentBlogJob={currentBlogJob}
              isGeneratingBusinessReport={isGeneratingBusinessReport}
              currentBusinessReportJob={currentBusinessReportJob}
            />

            {/* Generated Content List */}
            <StudioGeneratedContent
              signals={signals}
              savedPRDJobs={savedPRDJobs}
              setViewingPRDJob={setViewingPRDJob}
              downloadPRD={downloadPRD}
              savedMarketingStrategyJobs={savedMarketingStrategyJobs}
              setViewingMarketingStrategyJob={setViewingMarketingStrategyJob}
              downloadMarketingStrategy={downloadMarketingStrategy}
              savedBlogJobs={savedBlogJobs}
              setViewingBlogJob={setViewingBlogJob}
              downloadBlog={downloadBlog}
              savedBusinessReportJobs={savedBusinessReportJobs}
              setViewingBusinessReportJob={setViewingBusinessReportJob}
              downloadBusinessReport={downloadBusinessReport}
            />
          </div>
        </ScrollArea>
      </div>

      {/* Signal Picker Dialog */}
      <StudioSignalPicker
        open={pickerOpen}
        onOpenChange={setPickerOpen}
        selectedItem={selectedItem}
        selectedSignals={selectedSignals}
        onSelectSignal={triggerGeneration}
        getItemTitle={getItemTitle}
        getItemIcon={getItemIcon}
      />

      {/* All Studio Modals */}
      <StudioModals
        projectId={projectId}
        viewingPRDJob={viewingPRDJob}
        setViewingPRDJob={setViewingPRDJob}
        downloadPRD={downloadPRD}
        viewingMarketingStrategyJob={viewingMarketingStrategyJob}
        setViewingMarketingStrategyJob={setViewingMarketingStrategyJob}
        downloadMarketingStrategy={downloadMarketingStrategy}
        viewingBlogJob={viewingBlogJob}
        setViewingBlogJob={setViewingBlogJob}
        downloadBlog={downloadBlog}
        viewingBusinessReportJob={viewingBusinessReportJob}
        setViewingBusinessReportJob={setViewingBusinessReportJob}
        downloadBusinessReport={downloadBusinessReport}
      />
    </div>
  );
};
