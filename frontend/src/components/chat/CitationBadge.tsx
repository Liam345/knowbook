/**
 * CitationBadge Component
 *
 * Educational Note: Displays citation numbers with hover cards showing source content.
 * Uses lazy loading - content only fetched when user hovers.
 */

import { useState, useCallback } from 'react'
import { Badge } from '@/components/ui/badge'
import {
  HoverCard,
  HoverCardContent,
  HoverCardTrigger,
} from '@/components/ui/hover-card'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { FileText, CircleNotch } from '@phosphor-icons/react'
import { chatsAPI, CitationContent } from '@/lib/chats'

interface CitationBadgeProps {
  citationNumber: number
  chunkId: string
  sourceId: string
  pageNumber: number
  projectId: string
  sourceName?: string
}

export function CitationBadge({
  citationNumber,
  chunkId,
  sourceId: _sourceId, // Prefixed with _ to indicate intentionally unused
  pageNumber,
  projectId,
  sourceName,
}: CitationBadgeProps) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [chunkContent, setChunkContent] = useState<CitationContent | null>(null)
  const [hasLoaded, setHasLoaded] = useState(false)

  /**
   * Load citation content when hover card opens
   */
  const handleOpenChange = useCallback(
    async (open: boolean) => {
      // Only fetch once
      if (open && !hasLoaded && !loading) {
        setLoading(true)
        setError(null)

        try {
          const content = await chatsAPI.getCitationContent(projectId, chunkId)
          setChunkContent(content)
          setHasLoaded(true)
        } catch (err) {
          console.error('Failed to load citation:', err)
          setError('Failed to load citation content')
        } finally {
          setLoading(false)
        }
      }
    },
    [projectId, chunkId, hasLoaded, loading]
  )

  /**
   * Clean content for display - normalize whitespace
   */
  const cleanContent = (content: string): string => {
    return content
      .replace(/\n{3,}/g, '\n\n') // Multiple newlines → double newline
      .replace(/[ \t]+/g, ' ') // Normalize spaces
      .split('\n')
      .map((line) => line.trim())
      .join('\n')
      .trim()
  }

  return (
    <HoverCard openDelay={200} closeDelay={100} onOpenChange={handleOpenChange}>
      <HoverCardTrigger asChild>
        <Badge
          variant="default"
          className="cursor-pointer text-[11px] px-2 py-0.5 h-[18px] align-super hover:bg-primary/90"
        >
          {citationNumber}
        </Badge>
      </HoverCardTrigger>

      <HoverCardContent className="w-[28rem] p-0" side="top" align="start">
        <Card className="border-0 shadow-none">
          <CardHeader className="pb-2">
            <div className="flex items-center gap-2">
              <FileText size={16} className="text-primary" />
              <CardTitle className="text-sm">
                {chunkContent?.source_name || sourceName || 'Source'}
              </CardTitle>
            </div>
            <CardDescription className="text-xs">
              Page {chunkContent?.page_number || pageNumber}
              {chunkContent?.chunk_index !== undefined &&
                `, Section ${chunkContent.chunk_index + 1}`}
            </CardDescription>
          </CardHeader>
          <CardContent className="max-h-72 overflow-y-auto pt-0">
            {loading ? (
              <div className="flex items-center justify-center py-4">
                <CircleNotch size={14} className="animate-spin text-muted-foreground" />
                <span className="ml-2 text-sm text-muted-foreground">Loading...</span>
              </div>
            ) : error ? (
              <p className="text-sm text-destructive">{error}</p>
            ) : chunkContent ? (
              <p className="text-sm whitespace-pre-wrap text-muted-foreground">
                {cleanContent(chunkContent.content)}
              </p>
            ) : null}
          </CardContent>
        </Card>
      </HoverCardContent>
    </HoverCard>
  )
}
