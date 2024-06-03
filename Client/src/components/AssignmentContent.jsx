import React from 'react'
import { FaFileAlt } from 'react-icons/fa'
import { useState, useEffect } from 'react'
import api from '../api'
import '../styles/AssignmentContent.css'
import { useParams } from 'react-router-dom'
import { NavLink } from 'react-router-dom'

const AssignmentContent = () => {
    const [assignments, setAssignments] = useState([])
    const param = useParams()
    useEffect(() => {
        getAssignments()
    }, [])

    const getAssignments = () => {
        api.get(`/assignment/get_assignments/${param.id}/`)
            .then((res) => res.data)
            .then((data) => {
                setAssignments(data)
                console.log(data)
            })
            .catch((error) => {
                alert(error)
                console.log(error)
            })
    }

    let assignmentList = []
    assignments.map((item) => {
        assignmentList.push({
            id: item[0],
            title: item[1],
            description: item[12],
            status: item[9]
        })
    })

    return (
        <div className="assessment-list">
            <h2>Assessment</h2>
            {assignmentList.map((assignment) => (
                <div key={assignment.id} className="assessment-item">
                    <div className="assessment-header">
                        <FaFileAlt className="file-icon" />
                        <NavLink to={`/courses/assignment/${param.id}/${assignment.id}`}>
                            <span className="assessment-title">{assignment.title}</span>
                        </NavLink>
                    </div>
                    <div className="assessment-body">
                        <p className="assessment-description">{assignment.description}</p>
                        <p>{assignment.status}</p>
                    </div>
                </div>
            ))}
        </div>
    )
}

export default AssignmentContent
