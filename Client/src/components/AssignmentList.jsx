import React from 'react'
import '../styles/AssignmentList.css'
import { useState, useEffect } from 'react'
import api from '../api'

const AssignmentList = () => {
  const [courses, setCourses] = useState([])

  useEffect(() => {
    getCourses()
  }, [])

  const getCourses = () => {
    api.get('/assignment/get_courses/')
      .then((res) => res.data)
      .then((data) => {
        setCourses(data)
        console.log(data)
      })
      .catch((error) => {
        alert(error)
        console.log(error)
      })
  }

  const courseInfor = courses

  return (
    <div className='assignment--list'>
      <div className="list--header">
        <h2>Assignments</h2>
        <select>
          <option value="english">English</option>
          <option value="vietnam">VietNam</option>
        </select>
      </div>
      <div className="list--container">
        {courseInfor.map((course, i) => (
          <div className='list' key={i}>
            <div className="course--detail" key={i}>
              <h2>{course.title}</h2>
              <div className='course-total' key={i}>
                <span>Total: {course.total_assignments}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default AssignmentList
