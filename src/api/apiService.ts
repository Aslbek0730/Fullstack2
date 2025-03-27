import axiosClient from "./axiosClient"

// Generic GET request
export const fetchData = async (endpoint: string) => {
  try {
    const response = await axiosClient.get(endpoint)
    return response.data
  } catch (error) {
    console.error("Error fetching data:", error)
    throw error
  }
}

// Generic POST request
export const postData = async (endpoint: string, data: any) => {
  try {
    const response = await axiosClient.post(endpoint, data)
    return response.data
  } catch (error) {
    console.error("Error posting data:", error)
    throw error
  }
}

// Example of a specific API call
export const getCourses = () => {
  return fetchData("courses/")
}

// Example of a specific POST API call
export const createCourse = (courseData: any) => {
  return postData("courses/", courseData)
}

