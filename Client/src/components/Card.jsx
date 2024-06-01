import React from 'react'
import { BiCheck, BiCode, BiSolidWatch, BiStopwatch, BiX } from 'react-icons/bi'
import { useState, useEffect } from 'react'
import api from '../api'

const Card = () => {
    const [assignments, setAssignments] = useState([])

    useEffect(() => {
        getAssignments()
    }, [])

    const getAssignments = () => {
        api.get('/assignment/get_all_assignments/')
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

    const doneAssignment = () => {
        let done = []
        assignments.map((assignment) => {
            if (assignment[9] === 'Done') {
                done.push(assignment)
            }
        })
        return done.length
    }

    const generalInformation = [
        {
            title: 'Total',
            icon: <BiCode />,
            quantity: assignments.length
        },
        {
            title: 'Complete',
            icon: <BiCheck />,
            quantity: doneAssignment()
        },
        {
            title: 'Pending',
            icon: <BiStopwatch />,
            quantity: assignments.length - doneAssignment()
        },
        {
            title: 'Late',
            icon: <BiSolidWatch />,
            quantity: 0
        },
        {
            title: 'UnComplete',
            icon: <BiX />,
            quantity: 0
        }
    ]

    return (
        <div className="card--container">
            {generalInformation.map((item, i) => (
                <div className="card" key={i}>
                    <div className="card--cover" key={i}>{item.icon}</div>
                    <div className="card--title">
                        <h2>{item.title}</h2>
                        <span>{item.quantity}</span>
                    </div>
                </div>
            ))}
        </div>
    )
}

export default Card
