import { useState, useEffect } from 'react'
import Dashboard from '@/components/Dashboard'
import ProjectWorkspace from '@/components/ProjectWorkspace'
import { Project } from '@/types'

function App() {
  const [currentProject, setCurrentProject] = useState<Project | null>(null)

  return (
    <div className="h-screen bg-background">
      {currentProject ? (
        <ProjectWorkspace 
          project={currentProject} 
          onBackToDashboard={() => setCurrentProject(null)}
        />
      ) : (
        <Dashboard onOpenProject={setCurrentProject} />
      )}
    </div>
  )
}

export default App