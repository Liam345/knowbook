import { useState } from 'react'
import Dashboard from '@/components/Dashboard'
import ProjectWorkspace from '@/components/ProjectWorkspace'
import { Project } from '@/types'
import { ToastContainer, useToast } from '@/components/ui/toast'

function App() {
  const [currentProject, setCurrentProject] = useState<Project | null>(null)
  const { toasts, dismissToast } = useToast()

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
      
      {/* Toast notifications */}
      <ToastContainer toasts={toasts} onDismiss={dismissToast} />
    </div>
  )
}

export default App