import React from 'react'
import { BiBookAlt, BiHome, BiStats, BiTask, BiUser } from 'react-icons/bi'
import "../styles/Sidebar.css"
const Sidebar = () => {
  return (
    <div className='menu'>
      <div className="logo">
        <BiBookAlt className='logo-icon'/>
        <h2>Assignment</h2>
      </div>

      <div className="menu--list">
        <a href="/" className="item">
            <BiHome className='icon'/>
            Dashboard
        </a>
        <a href="/courses" className="item">
            <BiTask className='icon'/>
            Courses
        </a>
      </div>
    </div>
  )
}

export default Sidebar
