import axios from "axios"
import axiosClient from "./axiosClient"

const API_URL = "http://127.0.0.1:8000/api/v1/users/"

// Interface for login credentials
interface LoginCredentials {
  email: string
  password: string
}

// Interface for registration data
interface RegistrationData {
  email: string
  username: string
  password: string
  password_confirm: string
  first_name?: string
  last_name?: string
}

// Login function - uses direct axios to avoid interceptors during login
export const login = async (credentials: LoginCredentials) => {
  try {
    const response = await axios.post(`${API_URL}token/`, {
      email: credentials.email,
      password: credentials.password,
    })

    const { access, refresh } = response.data

    // Store tokens in localStorage
    localStorage.setItem("access_token", access)
    localStorage.setItem("refresh_token", refresh)

    return true
  } catch (error) {
    console.error("Login error:", error)
    throw error
  }
}

// Register function
export const register = async (userData: RegistrationData) => {
  try {
    const response = await axios.post(`${API_URL}`, userData)
    return response.data
  } catch (error) {
    console.error("Registration error:", error)
    throw error
  }
}

// Logout function
export const logout = () => {
  localStorage.removeItem("access_token")
  localStorage.removeItem("refresh_token")
  // Optionally redirect to login page
  window.location.href = "/login"
}

// Check if user is authenticated
export const isAuthenticated = () => {
  return !!localStorage.getItem("access_token")
}

// Get current user profile
export const getCurrentUser = async () => {
  try {
    const response = await axiosClient.get(`${API_URL}me/`)
    return response.data
  } catch (error) {
    console.error("Error fetching user profile:", error)
    throw error
  }
}

