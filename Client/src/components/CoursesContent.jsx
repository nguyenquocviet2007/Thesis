import React from 'react'
import { FaStar, FaLock, FaUnlock } from 'react-icons/fa'
import '../styles/CoursesContent.css'
import { useState, useEffect } from 'react'
import api from '../api'
import { NavLink } from 'react-router-dom'

const CoursesContent = () => {
    const [coursesInfor, setCoursesInfor] = useState([])

    useEffect(() => {
        getCoursesInfor()
    }, [])

    const getCoursesInfor = () => {
        api.get(`/assignment/get_courses/`)
            .then((res) => res.data)
            .then((data) => {
                setCoursesInfor(data)
                console.log(data)
            })
            .catch((error) => {
                alert(error)
                console.log(error)
            })
    }

    let courses = []
    coursesInfor.map((item) => {
        courses.push({
            id: item.id,
            course_code: item.course_code,
            title: item.title,
            instructors: item.lecturer
        })
    })

    return (
        <div className="course-list">
            {courses.map((course) => (
                <div key={course.id} className="course-item">
                    <div className="course-header">
                        <span className="course-code">{course.course_code}</span>
                        <FaStar className="star-icon" />
                    </div>
                    <div className="course-body">
                      <NavLink to={`/courses/assignment/${course.course_code}`}>
                        <h3 className="course-title">
                            {course.course_code.split('_')[0]} - {course.title}
                        </h3>
                      </NavLink>
                        <span className="course-info">{course.moreInfo}</span>
                    </div>
                    <div className="course-footer">
                        <span>Lecturer: {course.instructors}</span>
                    </div>
                </div>
            ))}
        </div>
    )
}

export default CoursesContent
