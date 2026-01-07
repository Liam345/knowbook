import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Plus, Gear } from '@phosphor-icons/react'
import { Project } from '@/types'
import { projectsApi } from '@/lib/api'
import CreateProjectDialog from '@/components/CreateProjectDialog'
import ProjectCard from '@/components/ProjectCard'

interface DashboardProps {
  onOpenProject: (project: Project) => void
}

export default function Dashboard({ onOpenProject }: DashboardProps) {
  const [projects, setProjects] = useState<Project[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [showCreateDialog, setShowCreateDialog] = useState(false)

  useEffect(() => {
    loadProjects()
  }, [])

  const loadProjects = async () => {
    try {
      setIsLoading(true)
      const projectsList = await projectsApi.getAll()
      setProjects(projectsList)
      setError('')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load projects')
    } finally {
      setIsLoading(false)
    }
  }

  const handleProjectCreated = (project: Project) => {
    setProjects(prev => [project, ...prev])
  }

  const handleProjectUpdate = (updatedProject: Project) => {
    setProjects(prev =>
      prev.map(p => (p.id === updatedProject.id ? updatedProject : p))
    )
  }

  const handleProjectDelete = (projectId: string) => {
    setProjects(prev => prev.filter(p => p.id !== projectId))
  }

  const handleOpenProject = async (project: Project) => {
    // Update last opened timestamp
    try {
      const updatedProject = await projectsApi.update(project.id, {})
      handleProjectUpdate(updatedProject)
      onOpenProject(updatedProject)
    } catch (err) {
      // If update fails, still open the project
      onOpenProject(project)
    }
  }

  if (isLoading) {
    return (
      <div className="h-screen flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
          <p className="text-muted-foreground">Loading projects...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="h-screen flex flex-col">
      {/* Header */}
      <header className="border-b bg-background">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-primary">KnowBook</h1>
              <p className="text-muted-foreground">Your AI-powered knowledge assistant</p>
            </div>
            <div className="flex items-center gap-2">
              <Button variant="outline" size="icon">
                <Gear size={20} />
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 container mx-auto px-6 py-8">
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {/* Create New Project Card */}
          <Card
            className="border-dashed border-2 hover:border-primary transition-colors cursor-pointer"
            onClick={() => setShowCreateDialog(true)}
          >
            <CardHeader className="text-center pb-2">
              <div className="mx-auto w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-2">
                <Plus size={24} className="text-primary" />
              </div>
              <CardTitle className="text-lg">Create New Project</CardTitle>
            </CardHeader>
            <CardContent className="text-center">
              <CardDescription>
                Start a new project to organize your sources and generate AI content
              </CardDescription>
            </CardContent>
          </Card>

          {/* Project Cards */}
          {projects.map((project) => (
            <ProjectCard
              key={project.id}
              project={project}
              onOpen={handleOpenProject}
              onUpdate={handleProjectUpdate}
              onDelete={handleProjectDelete}
            />
          ))}

          {/* Empty State */}
          {projects.length === 0 && (
            <div className="col-span-full text-center py-12">
              <div className="mx-auto w-16 h-16 bg-muted rounded-lg flex items-center justify-center mb-4">
                <Plus size={32} className="text-muted-foreground" />
              </div>
              <h3 className="text-lg font-semibold mb-2">No projects yet</h3>
              <p className="text-muted-foreground mb-4 max-w-sm mx-auto">
                Create your first project to start organizing your knowledge with AI
              </p>
              <Button onClick={() => setShowCreateDialog(true)}>
                <Plus size={16} className="mr-2" />
                Create Project
              </Button>
            </div>
          )}
        </div>
      </main>

      {/* Create Project Dialog */}
      <CreateProjectDialog
        open={showCreateDialog}
        onOpenChange={setShowCreateDialog}
        onProjectCreated={handleProjectCreated}
      />
    </div>
  )
}