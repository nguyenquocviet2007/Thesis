import React from 'react'
import Sidebar from '../components/Sidebar'
import AssignmentContent from '../components/AssignmentContent'
import '../styles/Assignment.css'

function Assignemt() {
    return (
        <div className="assignment">
            <Sidebar />
            <div className="assignment--content">
                <AssignmentContent />
            </div>
        </div>
    )
}

export default Assignemt;