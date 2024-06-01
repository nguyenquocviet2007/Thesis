import { useState } from "react";
import api from "../api";
import { useNavigate } from "react-router-dom";
import { ACCESS_TOKEN, REFRESH_TOKEN } from '../constant';
import Cookies from 'js-cookie'
import "../styles/Form.css"

function FormLogin({route}) {
    const [studentId, setStudentId] = useState("")
    const [password, setPassword] = useState("")
    const [loading, setLoading] = useState(false)
    const navigate = useNavigate()
    
    const handleSubmit = async (e) => {
        setLoading(true)
        e.preventDefault()

        try {
            const res = await api.post(route, {studentId, password})
            Cookies.set(ACCESS_TOKEN, res.data.access)
            Cookies.set(REFRESH_TOKEN, res.data.refresh)
            navigate("/")
        }
        catch (error) {
            alert(error)
        }
        finally {
            setLoading(false)
        }
    }
    
    return <form onSubmit={handleSubmit} className="form-container">
        <h1>Login</h1>
        <input 
            type="text" 
            className="form-input" 
            value={studentId} 
            onChange={(e) => setStudentId(e.target.value)}
            placeholder="Student ID"
        />
        <input 
            type="password" 
            className="form-input" 
            value={password} 
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Password"
        />
        <button className="form-button" type="submit">
            Login    
        </button>
    </form>
}

export default FormLogin