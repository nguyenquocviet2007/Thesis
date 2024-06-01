import React from 'react'
import ContentHeader from './ContentHeader'
import Card from './Card'
import AssignmentList from './AssignmentList'
import '../styles/Content.css'
const Content = () => {
  return (
    <div className='content'>
      <ContentHeader />
      <Card />
      <AssignmentList />
    </div>
  )
}

export default Content
