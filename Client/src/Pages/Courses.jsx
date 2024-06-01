import React from 'react'
import Sidebar from '../components/Sidebar'
import CoursesContent from '../components/CoursesContent'
import '../styles/Courses.css'

function Courses() {
    return (
        <div className="courses">
            <Sidebar />
            <div className="courses--content">
                <CoursesContent />
            </div>
        </div>
    )
}

export default Courses;
