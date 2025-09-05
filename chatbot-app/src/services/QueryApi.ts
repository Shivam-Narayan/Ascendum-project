import axios, { AxiosError } from "axios"
import API_BASE_URL from "../config"

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
})

// Add interceptor to inject token dynamically
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token")
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

export const askDocument = async (batchId: string, question: string) => {
  try {
    const response = await api.post(`/api/ask/${batchId}/`, { question })
    return response.data
  } catch (error) {
    const axiosError = error as AxiosError<{ message?: string }>
    console.error("Ask API Error:", axiosError)

    if (axiosError.response?.data) {
      throw axiosError.response.data
    }
    throw { message: "Something went wrong" }
  }
}
