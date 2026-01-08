/**
 * Source Upload Dialog Component - Handles file uploads
 * 
 * Educational Note: This component provides a clean file upload interface
 * with drag-and-drop support, file validation, and upload progress.
 * It follows modern UX patterns for file uploads.
 */
import { useState, useRef } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { 
  Upload, 
  File, 
  X, 
  Spinner,
  FileText,
  Image,
  MusicNote,
  Table
} from '@phosphor-icons/react'
import { Project, Source } from '@/types'

interface SourceUploadDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  project: Project
  onUploadSuccess: (source: Source) => void
}

// Allowed file types (matching backend)
const ALLOWED_EXTENSIONS = {
  document: ['.pdf', '.docx', '.pptx', '.txt', '.md'],
  image: ['.png', '.jpg', '.jpeg', '.webp', '.gif'],
  audio: ['.mp3', '.wav', '.m4a', '.ogg', '.flac'],
  data: ['.csv']
}

const getAllowedExtensions = (): string[] => {
  return Object.values(ALLOWED_EXTENSIONS).flat()
}

const getFileCategory = (filename: string): string => {
  const ext = '.' + filename.split('.').pop()?.toLowerCase()
  
  for (const [category, extensions] of Object.entries(ALLOWED_EXTENSIONS)) {
    if (extensions.includes(ext)) {
      return category
    }
  }
  return 'unknown'
}

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

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`
}

export function SourceUploadDialog({ 
  open, 
  onOpenChange, 
  project, 
  onUploadSuccess 
}: SourceUploadDialogProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')
  const [dragOver, setDragOver] = useState(false)
  
  const fileInputRef = useRef<HTMLInputElement>(null)

  const resetForm = () => {
    setSelectedFile(null)
    setName('')
    setDescription('')
    setError('')
    setDragOver(false)
  }

  const handleClose = () => {
    if (!uploading) {
      resetForm()
      onOpenChange(false)
    }
  }

  const validateFile = (file: File): string | null => {
    const allowedExtensions = getAllowedExtensions()
    const fileExt = '.' + file.name.split('.').pop()?.toLowerCase()
    
    if (!allowedExtensions.includes(fileExt)) {
      return `File type not supported. Allowed types: ${allowedExtensions.join(', ')}`
    }
    
    // 50MB limit
    if (file.size > 50 * 1024 * 1024) {
      return 'File size must be less than 50MB'
    }
    
    return null
  }

  const handleFileSelect = (file: File) => {
    const validation = validateFile(file)
    if (validation) {
      setError(validation)
      return
    }
    
    setError('')
    setSelectedFile(file)
    if (!name) {
      // Set default name to filename without extension
      setName(file.name.replace(/\.[^/.]+$/, ''))
    }
  }

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      handleFileSelect(file)
    }
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    
    const file = e.dataTransfer.files?.[0]
    if (file) {
      handleFileSelect(file)
    }
  }

  const handleUpload = async () => {
    if (!selectedFile) return
    
    setUploading(true)
    setError('')
    
    try {
      const formData = new FormData()
      formData.append('file', selectedFile)
      if (name.trim()) {
        formData.append('name', name.trim())
      }
      if (description.trim()) {
        formData.append('description', description.trim())
      }
      
      const response = await fetch(`/api/v1/projects/${project.id}/sources`, {
        method: 'POST',
        body: formData
      })
      
      if (response.ok) {
        const result = await response.json()
        if (result.success) {
          onUploadSuccess(result.source)
          resetForm()
          onOpenChange(false)
        } else {
          setError(result.error || 'Upload failed')
        }
      } else {
        const result = await response.json()
        setError(result.error || 'Upload failed')
      }
    } catch (err) {
      setError('Network error. Please try again.')
    } finally {
      setUploading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Add Source</DialogTitle>
          <DialogDescription>
            Upload a file to add to your project sources
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* File Upload Area */}
          <div>
            <Label>File</Label>
            {!selectedFile ? (
              <div
                className={`mt-2 border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors ${
                  dragOver ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'
                }`}
                onClick={() => fileInputRef.current?.click()}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
              >
                <Upload size={32} className="mx-auto mb-2 text-gray-400" />
                <p className="text-sm text-gray-600 mb-1">
                  Click to browse or drag and drop
                </p>
                <p className="text-xs text-gray-500">
                  PDF, DOCX, PPTX, TXT, MD, PNG, JPG, WEBP, MP3, WAV, CSV
                </p>
              </div>
            ) : (
              <div className="mt-2 border rounded-lg p-4">
                <div className="flex items-center gap-3">
                  {(() => {
                    const category = getFileCategory(selectedFile.name)
                    const IconComponent = getCategoryIcon(category)
                    return <IconComponent size={24} className="text-muted-foreground" />
                  })()}
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-sm truncate">{selectedFile.name}</p>
                    <p className="text-xs text-gray-500">
                      {formatFileSize(selectedFile.size)} • {getFileCategory(selectedFile.name)}
                    </p>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => setSelectedFile(null)}
                    className="h-8 w-8"
                  >
                    <X size={16} />
                  </Button>
                </div>
              </div>
            )}
            <input
              ref={fileInputRef}
              type="file"
              accept={getAllowedExtensions().join(',')}
              onChange={handleFileInput}
              className="hidden"
            />
          </div>

          {/* Name Input */}
          <div>
            <Label htmlFor="source-name">Name (optional)</Label>
            <Input
              id="source-name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Enter a custom name for this source"
              className="mt-2"
            />
          </div>

          {/* Description Input */}
          <div>
            <Label htmlFor="source-description">Description (optional)</Label>
            <Textarea
              id="source-description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Add a description for this source"
              className="mt-2 resize-none"
              rows={3}
            />
          </div>

          {/* Error Message */}
          {error && (
            <div className="text-sm text-red-600 bg-red-50 p-2 rounded">
              {error}
            </div>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={handleClose} disabled={uploading}>
            Cancel
          </Button>
          <Button 
            onClick={handleUpload} 
            disabled={!selectedFile || uploading}
          >
            {uploading && <Spinner size={16} className="mr-2 animate-spin" />}
            Upload
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}