import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Home from './Pages/Home'
import Login from './Pages/Login'
import Courses from './Pages/Courses'
import Assignment from './Pages/Assignment'
import AssignmentDetail from './Pages/AssignmentDetail'
import { ACCESS_TOKEN, REFRESH_TOKEN } from './constant'
import Cookies from 'js-cookie'
import ProtectedRoute from './components/ProtectedRoute'

function Logout() {
  Cookies.remove(ACCESS_TOKEN)
  Cookies.remove(REFRESH_TOKEN)
  return <Navigate to='/login'/>
}

const App = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route 
          path='/'
          element = {
            <ProtectedRoute>
              <Home />
            </ProtectedRoute>
          }
        />
        <Route 
          path='/courses'
          element = {
            <ProtectedRoute>
              <Courses />
            </ProtectedRoute>
          }
        />
        <Route 
          path='/courses/assignment/:id/'
          element = {
            <ProtectedRoute>
              <Assignment />
            </ProtectedRoute>
          }
        />
        <Route 
          path='/courses/assignment/:id/:assignmentid/'
          element = {
            <ProtectedRoute>
              <AssignmentDetail />
            </ProtectedRoute>
          }
        />
        <Route path="/login" element={<Login />}/>
        <Route path="/logout" element={<Logout />}/>
      </Routes>
    </BrowserRouter>
  )
}

export default App
