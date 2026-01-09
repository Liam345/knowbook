/**
 * Sources List Component - Displays list of project sources
 * 
 * Educational Note: This component handles the display of individual sources
 * with their status, file info, and actions. It's designed to match NoobBook's
 * clean and informative source list design.
 */
import { useState } from 'react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { 
  DotsThree,
  Download,
  Trash,
  Spinner,
  Check,
  Warning,
  Clock
} from '@phosphor-icons/react'
import { 
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Source } from '@/types'

interface SourcesListProps {
  sources: Source[]
  projectId: string
  onDeleteSource: (sourceId: string) => void
  getCategoryIcon: (category: string) => any
  getStatusColor: (status: string) => string
}

// Status indicators
const getStatusIndicator = (status: string) => {
  switch (status) {
    case 'ready':
      return <Check size={14} className="text-green-600" />
    case 'processing':
    case 'embedding':
      return <Spinner size={14} className="text-blue-600 animate-spin" />
    case 'failed':
      return <Warning size={14} className="text-red-600" />
    case 'uploaded':
    default:
      return <Clock size={14} className="text-gray-600" />
  }
}

// Status text
const getStatusText = (status: string) => {
  switch (status) {
    case 'ready':
      return 'Ready'
    case 'processing':
      return 'Processing...'
    case 'embedding':
      return 'Embedding...'
    case 'failed':
      return 'Failed'
    case 'uploaded':
    default:
      return 'Queued'
  }
}

// Format file size
const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`
}

// Format relative time
const formatRelativeTime = (dateString: string): string => {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffSeconds = Math.floor(diffMs / 1000)
  const diffMinutes = Math.floor(diffSeconds / 60)
  const diffHours = Math.floor(diffMinutes / 60)
  const diffDays = Math.floor(diffHours / 24)

  if (diffSeconds < 60) return 'Just now'
  if (diffMinutes < 60) return `${diffMinutes}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays < 7) return `${diffDays}d ago`
  
  return date.toLocaleDateString()
}

export function SourcesList({ 
  sources, 
  projectId,
  onDeleteSource, 
  getCategoryIcon, 
  getStatusColor 
}: SourcesListProps) {
  const [deletingIds, setDeletingIds] = useState<Set<string>>(new Set())

  const handleDelete = async (sourceId: string) => {
    setDeletingIds(prev => new Set(prev).add(sourceId))
    try {
      await onDeleteSource(sourceId)
    } finally {
      setDeletingIds(prev => {
        const newSet = new Set(prev)
        newSet.delete(sourceId)
        return newSet
      })
    }
  }

  const handleDownload = (source: Source, projectId: string) => {
    // Create download link - will be implemented with proper backend endpoint
    const downloadUrl = `/api/v1/projects/${projectId}/sources/${source.id}/download`
    window.open(downloadUrl, '_blank')
  }

  return (
    <div className="p-4 space-y-3">
      {sources.map((source, index) => {
        const CategoryIcon = getCategoryIcon(source.category || 'unknown')
        const isDeleting = deletingIds.has(source.id)
        
        return (
          <div key={source.id}>
            <Card className="p-3 hover:shadow-sm transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-3 flex-1 min-w-0">
                  {/* File Icon */}
                  <div className="mt-0.5">
                    <CategoryIcon size={16} className="text-muted-foreground" />
                  </div>
                  
                  {/* File Info */}
                  <div className="flex-1 min-w-0">
                    <h4 className="font-medium text-sm truncate mb-1">
                      {source.name}
                    </h4>
                    
                    {/* Status */}
                    <div className="flex items-center gap-2 mb-2">
                      {getStatusIndicator(source.status)}
                      <span className={`text-xs font-medium ${getStatusColor(source.status)}`}>
                        {getStatusText(source.status)}
                      </span>
                    </div>
                    
                    {/* File Details */}
                    <div className="text-xs text-muted-foreground space-y-1">
                      <div className="flex justify-between">
                        <span>{source.category?.toLowerCase() || 'unknown'}</span>
                        <span>{formatFileSize(source.file_size || 0)}</span>
                      </div>
                      <div>
                        <span>{formatRelativeTime(source.created_at)}</span>
                      </div>
                    </div>
                    
                    {/* Description */}
                    {source.description && (
                      <p className="text-xs text-muted-foreground mt-2 line-clamp-2">
                        {source.description}
                      </p>
                    )}
                  </div>
                </div>
                
                {/* Actions */}
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button 
                      variant="ghost" 
                      size="icon" 
                      className="h-8 w-8 ml-2"
                      disabled={isDeleting}
                    >
                      {isDeleting ? (
                        <Spinner size={14} className="animate-spin" />
                      ) : (
                        <DotsThree size={14} />
                      )}
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem onClick={() => handleDownload(source, projectId)}>
                      <Download size={14} className="mr-2" />
                      Download
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem 
                      className="text-red-600 focus:text-red-600"
                      onClick={() => handleDelete(source.id)}
                    >
                      <Trash size={14} className="mr-2" />
                      Delete
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            </Card>
            
            {index < sources.length - 1 && <Separator className="my-3" />}
          </div>
        )
      })}
    </div>
  )
}