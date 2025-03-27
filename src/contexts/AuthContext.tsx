"use client"

import type React from "react"
import { createContext, useContext, useState, useEffect, type ReactNode } from "react"
import { getCurrentUser, isAuthenticated, logout } from "../api/authService"

interface User {
  id: number
  email: string
  username: string
  first_name?: string
  last_name?: string
  // Add other user properties as needed
}

interface AuthContextType {
  user: User | null
  loading: boolean
  isAuthenticated: boolean
  logout: () => void
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  const refreshUser = async () => {
    if (!isAuthenticated()) {
      setUser(null)
      return
    }

    try {
      const userData = await getCurrentUser()
      setUser(userData)
    } catch (error) {
      console.error("Failed to fetch user data:", error)
      setUser(null)
    }
  }

  useEffect(() => {
    const initAuth = async () => {
      setLoading(true)
      await refreshUser()
      setLoading(false)
    }

    initAuth()
  }, [])

  const value = {
    user,
    loading,
    isAuthenticated: !!user,
    logout,
    refreshUser,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}

