import React from 'react';

const ExamSchedule = () => {
  const exams = [
    { date: '28/02/2025', day: 'Friday', branch: 'CSE, IT, CSCE, CSSE', subject: 'Universal Human Values (HS30401)' },
    { date: '01/03/2025', day: 'Saturday', branch: 'CSE', subject: 'Artificial Intelligence (CS30002)' },
    { date: '01/03/2025', day: 'Saturday', branch: 'IT', subject: 'Data Science and Analytics (CS30004)' },
    { date: '01/03/2025', day: 'Saturday', branch: 'CSCE', subject: 'Wireless Mobile Communication (EC30002)' },
    { date: '01/03/2025', day: 'Saturday', branch: 'CSSE', subject: 'ARM and Advanced Microprocessors (EC30007)' },
    { date: '03/03/2025', day: 'Monday', branch: 'CSE, IT', subject: 'Machine Learning (CS31002)' },
    { date: '03/03/2025', day: 'Monday', branch: 'CSCE', subject: 'Block Chain (CS40012)' },
    { date: '03/03/2025', day: 'Monday', branch: 'CSSE', subject: 'Compilers (CS30006)' },
    { date: '04/03/2025', day: 'Tuesday', branch: 'CSE, IT', subject: 'Cloud Computing (CS30010)/ Software Project Management (CS30036)' },
    { date: '04/03/2025', day: 'Tuesday', branch: 'CSCE', subject: 'Cloud Computing (CS30010)' },
    { date: '04/03/2025', day: 'Tuesday', branch: 'CSSE', subject: 'Data Mining and Data Warehousing (CS30013)' },
    { date: '06/03/2025', day: 'Thursday', branch: 'CSE, IT, CSCE, CSSE', subject: 'Open Elective-II/MI-1' },
  ];

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h2 style={{ color: '#2E7D32' }}>Mid Semester Exam Schedule - Spring 2025</h2>
      <h3 style={{ color: '#388E3C' }}>Examination Time: 03:30 PM - 05:00 PM</h3>
      <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '10px' }}>
        <thead>
          <tr style={{ backgroundColor: '#E8F5E9', color: '#2E7D32' }}>
            <th style={cellStyle}>Date</th>
            <th style={cellStyle}>Day</th>
            <th style={cellStyle}>Branch</th>
            <th style={cellStyle}>Subject</th>
          </tr>
        </thead>
        <tbody>
          {exams.map((exam, index) => (
            <tr key={index} style={{ backgroundColor: index % 2 === 0 ? '#FFFFFF' : '#F1F8E9' }}>
              <td style={cellStyle}>{exam.date}</td>
              <td style={cellStyle}>{exam.day}</td>
              <td style={cellStyle}>{exam.branch}</td>
              <td style={cellStyle}>{exam.subject}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

const cellStyle = {
  padding: '10px',
  borderBottom: '1px solid #e0e0e0',
  textAlign: 'left',
};

export default ExamSchedule;