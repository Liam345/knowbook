import { Button } from '@/components/ui/button'
import { ArrowLeft } from '@phosphor-icons/react'
import { Project } from '@/types'
import SourcesPanel from './SourcesPanel'
import ChatPanel from './ChatPanel'

interface ProjectWorkspaceProps {
  project: Project
  onBackToDashboard: () => void
}

export default function ProjectWorkspace({ project, onBackToDashboard }: ProjectWorkspaceProps) {
  return (
    <div className="h-screen flex flex-col">
      {/* Header */}
      <header className="border-b bg-background">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" onClick={onBackToDashboard}>
              <ArrowLeft size={20} />
            </Button>
            <div>
              <h1 className="text-xl font-bold">{project.name}</h1>
              {project.description && (
                <p className="text-sm text-muted-foreground">{project.description}</p>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Workspace */}
      <div className="flex-1 flex">
        {/* Sources Panel */}
        <SourcesPanel project={project} />

        {/* Chat Panel */}
        <ChatPanel project={project} />

        {/* Studio Panel */}
        <div className="w-80 border-l bg-muted/20 p-4">
          <h2 className="font-semibold mb-4">Studio</h2>
          <div className="text-center py-8 text-muted-foreground">
            <p>Generate content</p>
            <p className="text-sm">Create documents, presentations, and more</p>
          </div>
        </div>
      </div>
    </div>
  )
}