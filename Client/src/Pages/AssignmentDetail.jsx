import Sidebar from "../components/Sidebar";
import AssignmentDetailContent from "../components/AssignmentDetailContent"
import '../styles/AssignmentDetail.css'
import { useState, useEffect } from 'react'
import api from '../api'
import { useParams } from 'react-router-dom'
function AssignmentDetail() {
    const [assignment, setAssignment] = useState([])
    const param = useParams()
    useEffect(() => {
        getAssignment()
    }, [])

    const getAssignment = () => {
        api.get(`/assignment/get_assignment/${param.assignmentid}/`)
            .then((res) => res.data)
            .then((data) => {
                setAssignment(data)
                console.log(data)
            })
            .catch((error) => {
                alert(error)
                console.log(error)
            })
    }
    return (
        <div className="detail">
            <Sidebar />
            <div className="detail--content">
            {assignment.map((assignment) => (
                <AssignmentDetailContent assignment={assignment} key={assignment.id} />
            ))}
            </div>
        </div>
    )
}

export default AssignmentDetail;