/**
 * Sources Panel Component - Manages project sources UI
 * 
 * Educational Note: This component provides the complete source management interface
 * including file uploads, source list display, and status tracking.
 * It follows NoobBook's design patterns with real-time status updates.
 */
import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import { 
  Plus, 
  File, 
  FileText, 
  Image, 
  MusicNote, 
  Table,
  DotsThree,
  Upload,
  Spinner
} from '@phosphor-icons/react'
import { Project, Source } from '@/types'
import { SourceUploadDialog } from './SourceUploadDialog'
import { SourcesList } from './SourcesList'

interface SourcesPanelProps {
  project: Project
}

// Icon mapping by file category
const getCategoryIcon = (category: string) => {
  switch (category) {
    case 'document':
      return FileText
    case 'image':
      return Image
    case 'audio':
      return MusicNote
    case 'data':
      return Table
    default:
      return File
  }
}

// Status colors matching NoobBook
const getStatusColor = (status: string) => {
  switch (status) {
    case 'ready':
      return 'text-green-600'
    case 'processing':
    case 'embedding':
      return 'text-blue-600'
    case 'failed':
      return 'text-red-600'
    case 'uploaded':
    default:
      return 'text-gray-600'
  }
}

export default function SourcesPanel({ project }: SourcesPanelProps) {
  const [sources, setSources] = useState<Source[]>([])
  const [loading, setLoading] = useState(true)
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false)
  const [refreshing, setRefreshing] = useState(false)

  // Load sources on component mount
  useEffect(() => {
    loadSources()
  }, [project.id])

  // Auto-refresh for processing sources every 2 seconds
  useEffect(() => {
    const hasProcessingSources = sources.some(s => 
      s.status === 'processing' || s.status === 'embedding'
    )
    
    if (!hasProcessingSources) return

    const interval = setInterval(() => {
      loadSources(true) // Silent refresh
    }, 2000)

    return () => clearInterval(interval)
  }, [sources])

  const loadSources = async (silent = false) => {
    try {
      if (!silent) setLoading(true)
      
      const response = await fetch(`/api/v1/projects/${project.id}/sources`)
      if (response.ok) {
        const data = await response.json()
        setSources(data.sources || [])
      } else {
        console.error('Failed to load sources')
      }
    } catch (error) {
      console.error('Error loading sources:', error)
    } finally {
      if (!silent) setLoading(false)
    }
  }

  const handleUploadSuccess = (newSource: Source) => {
    // Add new source to the top of the list
    setSources(prev => [newSource, ...prev])
    setUploadDialogOpen(false)
  }

  const handleDeleteSource = async (sourceId: string) => {
    try {
      const response = await fetch(`/api/v1/projects/${project.id}/sources/${sourceId}`, {
        method: 'DELETE'
      })
      
      if (response.ok) {
        setSources(prev => prev.filter(s => s.id !== sourceId))
      } else {
        console.error('Failed to delete source')
      }
    } catch (error) {
      console.error('Error deleting source:', error)
    }
  }

  const handleRefresh = () => {
    setRefreshing(true)
    loadSources().finally(() => setRefreshing(false))
  }

  // Get summary statistics
  const sourceStats = {
    total: sources.length,
    ready: sources.filter(s => s.status === 'ready').length,
    processing: sources.filter(s => s.status === 'processing' || s.status === 'embedding').length,
    failed: sources.filter(s => s.status === 'failed').length
  }

  if (loading) {
    return (
      <div className="w-80 border-r bg-muted/20 p-4">
        <div className="flex items-center justify-center h-32">
          <Spinner className="animate-spin" size={24} />
        </div>
      </div>
    )
  }

  return (
    <div className="w-80 border-r bg-muted/20 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b bg-background/50">
        <div className="flex items-center justify-between mb-3">
          <h2 className="font-semibold">Sources</h2>
          <div className="flex items-center gap-1">
            <Button 
              variant="ghost" 
              size="icon" 
              onClick={handleRefresh}
              disabled={refreshing}
              className="h-8 w-8"
            >
              <DotsThree 
                size={16} 
                className={refreshing ? 'animate-spin' : ''} 
              />
            </Button>
            <Button 
              variant="ghost" 
              size="icon"
              onClick={() => setUploadDialogOpen(true)}
              className="h-8 w-8"
            >
              <Plus size={16} />
            </Button>
          </div>
        </div>
        
        {/* Stats */}
        {sources.length > 0 && (
          <div className="text-xs text-muted-foreground space-y-1">
            <div className="flex justify-between">
              <span>Total sources:</span>
              <span className="font-medium">{sourceStats.total}</span>
            </div>
            <div className="flex justify-between">
              <span>Ready:</span>
              <span className="font-medium text-green-600">{sourceStats.ready}</span>
            </div>
            {sourceStats.processing > 0 && (
              <div className="flex justify-between">
                <span>Processing:</span>
                <span className="font-medium text-blue-600">{sourceStats.processing}</span>
              </div>
            )}
            {sourceStats.failed > 0 && (
              <div className="flex justify-between">
                <span>Failed:</span>
                <span className="font-medium text-red-600">{sourceStats.failed}</span>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Sources List */}
      <div className="flex-1 overflow-hidden">
        {sources.length === 0 ? (
          <div className="p-4">
            <div className="text-center py-8 text-muted-foreground">
              <Upload size={32} className="mx-auto mb-3 opacity-50" />
              <p className="font-medium mb-1">No sources yet</p>
              <p className="text-sm mb-4">Upload documents to get started</p>
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => setUploadDialogOpen(true)}
              >
                <Plus size={16} className="mr-2" />
                Add Source
              </Button>
            </div>
          </div>
        ) : (
          <ScrollArea className="h-full">
            <SourcesList 
              sources={sources}
              projectId={project.id}
              onDeleteSource={handleDeleteSource}
              getCategoryIcon={getCategoryIcon}
              getStatusColor={getStatusColor}
            />
          </ScrollArea>
        )}
      </div>

      {/* Upload Dialog */}
      <SourceUploadDialog
        open={uploadDialogOpen}
        onOpenChange={setUploadDialogOpen}
        project={project}
        onUploadSuccess={handleUploadSuccess}
      />
    </div>
  )
}