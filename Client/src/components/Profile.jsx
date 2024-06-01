import React from 'react'
import ProfileHeader from './ProfileHeader'
import '../styles/Profile.css'
import userImage from '../assets/default.jpg'
import { BiCodeBlock } from 'react-icons/bi'
import { useState, useEffect } from 'react'
import api from '../api'

const Profile = () => {
    const [profile, setProfile] = useState([])
    const [courses, setCourses] = useState([])

    useEffect(() => {
        getProfile()
    }, [])

    useEffect(() => {
        getCourses()
    }, [])

    const getProfile = () => {
        api.get('/user/get_profile/')
            .then((res) => res.data)
            .then((data) => {
                setProfile(data)
                console.log(data)
            })
            .catch((error) => {
                alert(error)
                console.log(error)
            })
    }

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

    const profileInfor = {
        fullname: profile.fullname,
        id: profile.student_id
    }

    let coursesInfor = []
    courses.map((item) => {
        coursesInfor.push({
            title: item.title,
            icon: <BiCodeBlock />
        })
    })

    return (
        <div className="profile">
            <ProfileHeader />
            <div className="user--profile">
                <div className="user--detail">
                    <img src={userImage} alt="" />
                    <h3 className="username">{profileInfor.fullname}</h3>
                    <span className="studentId">{profileInfor.id}</span>
                </div>
                <div className="user-courses">
                    {coursesInfor.map((course, i) => (
                        <div className="course" key={i}>
                            <div className="course-detail" key={i}>
                                <div className="course-cover" key={i}>
                                    {course.icon}
                                </div>
                                <div className="course-name">
                                    <h5 className="title" key={i}>
                                        {course.title}
                                    </h5>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    )
}

export default Profile
