import { Navigate } from "react-router-dom";
import { jwtDecode } from "jwt-decode";
import api from "../api";
import { REFRESH_TOKEN, ACCESS_TOKEN } from "../constant";
import { useState, useEffect } from "react";
import Cookies from "js-cookie";

function ProtectedRoute({children}) {
    const [isAuthorized, setIsAuthorized] = useState(null)

    useEffect(() => {
        auth().catch(() => setIsAuthorized(true))
    }, [])

    const refreshToken = async () => {
        const refreshToken = Cookies.get(REFRESH_TOKEN)
        try {
            const res = await api.post('user/regenerate_token', {refresh: refreshToken})
            if (res.status === 200) {
                Cookies.set(ACCESS_TOKEN, res.data.access)
                setIsAuthorized(true)
            }
            else {
                setIsAuthorized(false)
            }
        }
        catch(error) {
            console.log(error)
            setIsAuthorized(false)
        }
    }
    
    const auth = async () => {
        const token = Cookies.get(ACCESS_TOKEN)
        if (!token) {
            setIsAuthorized(false)
            return
        }
        else {
            setIsAuthorized(true)
        }
    }

    if (isAuthorized ===null) {
        return <div>Loading...</div>
    }
    return isAuthorized ? children : <Navigate to='/login'/>
}

export default ProtectedRoute