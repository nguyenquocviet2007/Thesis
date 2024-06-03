import React from 'react'
import { useState, useEffect } from 'react'
import api from '../api'
import { useParams } from 'react-router-dom'
import '../styles/AssignmentDetailContent.css'

const AssignmentDetailContent = ({ assignment }) => {
    const [file, setFile] = useState(null)
    const [msg, setMsg] = useState(null)
    const [answer, setAnswer] = useState([] || '')
    const [progress, setProgress] = useState({ started: false, pc: 0 })
    const [result, setResult] = useState([])
    const param = useParams()
    const handleChange = (e) => {
        const { id, value } = e.target

        setAnswer((prev) => ({ ...prev, [id]: value }))
    }
    const submitAssignment = (e) => {
        e.preventDefault()
        if (!file) {
            setMsg('No file selected')
            return
        }

        const formData = new FormData()
        formData.append('file', file)
        setMsg('Uploading...!')
        setProgress((prevState) => {
            return { ...prevState, started: true }
        })
        api.put(`/assignment/submit_assignment/${assignment.id}`, formData, {
            onUploadProgress: (progressEvent) => {
                setProgress((prevState) => {
                    return { ...prevState, pc: progressEvent.progress * 100 }
                })
            },
            headers: {
                'content-type': 'multipart/form-data'
            }
        }).then((res) => {
            if (res.status === 201) {
                setMsg('Upload Successfully!')
                console.log(res.data)
            }
        })
    }
    const submitAnswer = (e) => {
        if (!answer) {
            setMsg('Please answer question')
        }
        e.preventDefault()

        api.put(`/assignment/submit_answer/${param.assignmentid}`, Object.values(answer), {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            }
        })
            .then((res) => {
                if (res.status === 201) {
                    setMsg('Submit Successfully!')
                }
            })
            .catch((error) => {
                setMsg('Submit Faile!')
                console.log(error)
            })

        api.put(`/assignment/get_result/${param.assignmentid}/`)
            .then((res) => res.data)
            .then((data) => {
                setResult(data)
                console.log(data)
            })
            .catch((error) => alert(error))
    }

    const ProgressBar = ({ score, maxScore }) => {
        const percentage = Math.round((score / maxScore) * 100);
        return (
          <div className="progress-bar">
            <div
              className="progress"
              style={{ width: `${percentage}%` }}
              title={`Score: ${score} / ${maxScore}`}
            ></div>
          </div>
        );
      };

    if (assignment.question == null) {
        return (
            <div className="submit-assignment-container">
                <h2>Assignment Information</h2>
                <div className="assignment-info">
                    <div className="points-possible">
                        <strong>Points Possible</strong>
                        <div className="points">100</div>
                    </div>
                    <p>{assignment.description}</p>
                </div>
                <h2>Assignment Submission</h2>
                <form onSubmit={submitAssignment}>
                    <div className="file-input-container">
                        <span>Upload File: </span>
                        <input
                            type="file"
                            id="file"
                            name="file"
                            required
                            onChange={(e) => setFile(e.target.files[0])}
                        />
                    </div>
                    <br />
                    <button className="submit-button">
                        <p className="submit">submit</p>
                    </button>
                </form>
                {progress.started && <progress max="100" value={progress.pc}></progress>}
                {msg && <span>{msg}</span>}
            </div>
        )
    } else if (assignment.user_answer == null) {
        const questionList = []
        assignment.question.forEach((question, index) => {
            questionList.push(
                <div key={index}>
                    <h2>{question}</h2>
                    <input
                        className="input-text"
                        type="text"
                        onChange={handleChange}
                        key={index}
                        id={index}
                        value={answer[index] || ''}
                    />
                </div>
            )
        })
        return (
            <div className="question-wrapper">
                <div className="question-container">
                    <>
                        <form onSubmit={submitAnswer}>
                            {questionList}
                            <div className="footer">
                                <button className="btn">Submit</button>
                            </div>
                        </form>
                        {msg && <span>{msg}</span>}
                    </>
                </div>
            </div>
        )
    } else {
        const resultList = []
        assignment.question.forEach((question, index) => {
            resultList.push(
                <div className="result-details" key={index}>
                    <span className="question">{question}</span>
                    <p className="result"><span className='bold'>Your Answer: </span>{assignment.user_answer[index]}</p>
                    <p className="actual_answer"><span className='bold'>Actual Answer: </span>{assignment.answer[index]}</p>
                    <p className="explain"><span className='bold'>Explain: </span>{assignment.reason[index]}</p>
                    <p className='score'>Score: {assignment.result[index]} / 10</p>
                    {assignment.result[index] && <ProgressBar score={assignment.result[index]} maxScore='10'/>}
                    <br />
                    <div className="horizontal-line"></div>
                </div>
            )
        })
        return (
            <div className="question-wrapper">
                <div className="question-container">
                    <>{resultList}</>
                </div>
            </div>
        )
    }
}

export default AssignmentDetailContent
