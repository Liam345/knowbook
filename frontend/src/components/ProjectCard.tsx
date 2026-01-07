import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { DotsThree, Trash, PencilSimple } from '@phosphor-icons/react'
import { Project } from '@/types'
import { formatDate } from '@/lib/utils'
import { projectsApi } from '@/lib/api'

interface ProjectCardProps {
  project: Project
  onOpen: (project: Project) => void
  onUpdate: (project: Project) => void
  onDelete: (projectId: string) => void
}

export default function ProjectCard({ project, onOpen, onUpdate, onDelete }: ProjectCardProps) {
  const [isDeleting, setIsDeleting] = useState(false)

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this project? This action cannot be undone.')) {
      return
    }

    setIsDeleting(true)
    try {
      await projectsApi.delete(project.id)
      onDelete(project.id)
    } catch (err) {
      console.error('Failed to delete project:', err)
      alert('Failed to delete project. Please try again.')
    } finally {
      setIsDeleting(false)
    }
  }

  const handleOpen = () => {
    onOpen(project)
  }

  return (
    <Card className="hover:shadow-md transition-shadow cursor-pointer group">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex-1 min-w-0" onClick={handleOpen}>
            <CardTitle className="text-lg truncate">{project.name}</CardTitle>
            <CardDescription className="mt-1 line-clamp-2">
              {project.description || 'No description'}
            </CardDescription>
          </div>
          
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                className="opacity-0 group-hover:opacity-100 transition-opacity"
              >
                <DotsThree size={20} />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={handleOpen}>
                Open Project
              </DropdownMenuItem>
              <DropdownMenuItem>
                <PencilSimple size={16} className="mr-2" />
                Edit
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                className="text-red-600 focus:text-red-600"
                onClick={handleDelete}
                disabled={isDeleting}
              >
                <Trash size={16} className="mr-2" />
                {isDeleting ? 'Deleting...' : 'Delete'}
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </CardHeader>
      
      <CardContent onClick={handleOpen}>
        <div className="space-y-2 text-sm text-muted-foreground">
          <div className="flex justify-between">
            <span>Sources:</span>
            <span>{project.stats.sources_count}</span>
          </div>
          <div className="flex justify-between">
            <span>Chats:</span>
            <span>{project.stats.chats_count}</span>
          </div>
          <div className="flex justify-between">
            <span>Last opened:</span>
            <span>{formatDate(project.last_opened)}</span>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}