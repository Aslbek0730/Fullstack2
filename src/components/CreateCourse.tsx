"use client"

import type React from "react"
import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { createCourse } from "../api/apiService"

interface CourseFormData {
  title: string
  description: string
  short_description: string
  category: number
  level: string
  duration: string
  prerequisites: string
  learning_objectives: string[]
}

const CreateCourse: React.FC = () => {
  const [formData, setFormData] = useState<CourseFormData>({
    title: "",
    description: "",
    short_description: "",
    category: 1, // Default category ID
    level: "beginner",
    duration: "",
    prerequisites: "",
    learning_objectives: [""],
  })

  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }))
  }

  const handleObjectiveChange = (index: number, value: string) => {
    const updatedObjectives = [...formData.learning_objectives]
    updatedObjectives[index] = value
    setFormData((prev) => ({
      ...prev,
      learning_objectives: updatedObjectives,
    }))
  }

  const addObjective = () => {
    setFormData((prev) => ({
      ...prev,
      learning_objectives: [...prev.learning_objectives, ""],
    }))
  }

  const removeObjective = (index: number) => {
    const updatedObjectives = [...formData.learning_objectives]
    updatedObjectives.splice(index, 1)
    setFormData((prev) => ({
      ...prev,
      learning_objectives: updatedObjectives,
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
    setError(null)

    try {
      // Filter out empty objectives
      const filteredData = {
        ...formData,
        learning_objectives: formData.learning_objectives.filter((obj) => obj.trim() !== ""),
      }

      await createCourse(filteredData)
      navigate("/dashboard/courses") // Redirect to courses page after successful creation
    } catch (err: any) {
      const errorData = err.response?.data
      if (typeof errorData === "object") {
        // Extract first error message from each field
        const firstError = Object.entries(errorData)
          .map(([field, errors]) => `${field}: ${Array.isArray(errors) ? errors[0] : errors}`)
          .join(", ")
        setError(firstError)
      } else {
        setError("Failed to create course. Please try again.")
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="mx-auto max-w-3xl p-4">
      <h1 className="mb-6 text-2xl font-bold">Create New Course</h1>

      {error && <div className="mb-4 rounded-md bg-destructive/15 p-3 text-sm text-destructive">{error}</div>}

      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label htmlFor="title" className="mb-2 block text-sm font-medium">
            Course Title
          </label>
          <input
            id="title"
            name="title"
            value={formData.title}
            onChange={handleChange}
            required
            className="w-full rounded-md border border-input bg-background px-3 py-2"
          />
        </div>

        <div>
          <label htmlFor="short_description" className="mb-2 block text-sm font-medium">
            Short Description
          </label>
          <input
            id="short_description"
            name="short_description"
            value={formData.short_description}
            onChange={handleChange}
            required
            maxLength={255}
            className="w-full rounded-md border border-input bg-background px-3 py-2"
          />
        </div>

        <div>
          <label htmlFor="description" className="mb-2 block text-sm font-medium">
            Full Description
          </label>
          <textarea
            id="description"
            name="description"
            value={formData.description}
            onChange={handleChange}
            required
            rows={5}
            className="w-full rounded-md border border-input bg-background px-3 py-2"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label htmlFor="category" className="mb-2 block text-sm font-medium">
              Category
            </label>
            <select
              id="category"
              name="category"
              value={formData.category}
              onChange={handleChange}
              required
              className="w-full rounded-md border border-input bg-background px-3 py-2"
            >
              <option value={1}>Web Development</option>
              <option value={2}>Data Science</option>
              <option value={3}>Mobile Development</option>
              {/* Add more categories as needed */}
            </select>
          </div>

          <div>
            <label htmlFor="level" className="mb-2 block text-sm font-medium">
              Level
            </label>
            <select
              id="level"
              name="level"
              value={formData.level}
              onChange={handleChange}
              required
              className="w-full rounded-md border border-input bg-background px-3 py-2"
            >
              <option value="beginner">Beginner</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
            </select>
          </div>
        </div>

        <div>
          <label htmlFor="duration" className="mb-2 block text-sm font-medium">
            Duration (e.g., "8 weeks")
          </label>
          <input
            id="duration"
            name="duration"
            value={formData.duration}
            onChange={handleChange}
            className="w-full rounded-md border border-input bg-background px-3 py-2"
          />
        </div>

        <div>
          <label htmlFor="prerequisites" className="mb-2 block text-sm font-medium">
            Prerequisites
          </label>
          <textarea
            id="prerequisites"
            name="prerequisites"
            value={formData.prerequisites}
            onChange={handleChange}
            rows={3}
            className="w-full rounded-md border border-input bg-background px-3 py-2"
          />
        </div>

        <div>
          <div className="mb-2 flex items-center justify-between">
            <label className="text-sm font-medium">Learning Objectives</label>
            <button
              type="button"
              onClick={addObjective}
              className="rounded-md bg-primary px-2 py-1 text-xs font-medium text-primary-foreground"
            >
              Add Objective
            </button>
          </div>

          {formData.learning_objectives.map((objective, index) => (
            <div key={index} className="mb-2 flex items-center gap-2">
              <input
                value={objective}
                onChange={(e) => handleObjectiveChange(index, e.target.value)}
                className="flex-1 rounded-md border border-input bg-background px-3 py-2"
                placeholder={`Objective ${index + 1}`}
              />
              {formData.learning_objectives.length > 1 && (
                <button
                  type="button"
                  onClick={() => removeObjective(index)}
                  className="rounded-md bg-destructive/10 px-2 py-1 text-xs font-medium text-destructive"
                >
                  Remove
                </button>
              )}
            </div>
          ))}
        </div>

        <div className="flex justify-end gap-4">
          <button
            type="button"
            onClick={() => navigate("/dashboard/courses")}
            className="rounded-md border border-input bg-background px-4 py-2 text-sm font-medium"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={isSubmitting}
            className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground disabled:opacity-50"
          >
            {isSubmitting ? "Creating..." : "Create Course"}
          </button>
        </div>
      </form>
    </div>
  )
}

export default CreateCourse

