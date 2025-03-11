import React from 'react';

const HolidayList = () => {
  const holidays = [
    { date: '26.01.2024', day: 'Friday', event: 'REPUBLIC DAY' },
    { date: '14.02.2024', day: 'Wednesday', event: 'BASANTA PANCHAMI' },
    { date: '05.03.2024', day: 'Tuesday', event: 'PANCHAYATIRAJ DIWAS' },
    { date: '08.03.2024', day: 'Friday', event: 'MAHA SHIVRATRI' },
    { date: '26.03.2024', day: 'Tuesday', event: 'HOLI' },
    { date: '29.03.2024', day: 'Friday', event: 'GOOD FRIDAY' },
    { date: '01.04.2024', day: 'Monday', event: 'UTKAL DIVAS' },
    { date: '11.04.2024', day: 'Thursday', event: 'ID-UL-FITRE' },
    { date: '17.04.2024', day: 'Wednesday', event: 'RAM NAVAMI' },
    { date: '17.06.2024', day: 'Monday', event: 'ID-UL-JUHA' },
    { date: '17.07.2024', day: 'Wednesday', event: 'MUHARRAM' },
    { date: '15.08.2024', day: 'Thursday', event: 'INDEPENDENCE DAY' },
    { date: '26.08.2024', day: 'Monday', event: 'JANAMASTAMI' },
    { date: '16.09.2024', day: 'Monday', event: 'BIRTHDAY OF PROPHET MOHAMMMAD' },
    { date: '02.10.2024', day: 'Wednesday', event: 'GANDHI JAYANTI' },
    { date: '10.10.2024 - 16.10.2024', day: 'Thursday-Wednesday', event: 'DURGA PUJA – KUMAR PURNIMA' },
    { date: '31.10.2024', day: 'Thursday', event: 'KALIPUJA & DIWALI' },
    { date: '15.11.2024', day: 'Friday', event: 'KARTIKA PURNIMA/ GURU NANAK’S BIRTHDAY' },
    { date: '25.12.2024', day: 'Wednesday', event: 'CHRISTMAS' },
  ];

  const weekendFestivals = [
    { date: '14.04.2024', day: 'Sunday', event: 'MAHA VISHUBHA SANKRANTI' },
    { date: '15.06.2024', day: 'Saturday', event: 'RAJA SANKRANTI' },
    { date: '07.07.2024', day: 'Sunday', event: 'RATH YATRA' },
    { date: '07.09.2024', day: 'Saturday', event: 'GANESH PUJA' },
    { date: '08.09.2024', day: 'Sunday', event: 'NUAKHAI' },
  ];

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h2 style={{ color: '#2E7D32' }}>Holiday List for 2024</h2>
      <h3>Regular Holidays</h3>
      <table style={{ width: '100%', borderCollapse: 'collapse', marginBottom: '20px' }}>
        <thead>
          <tr style={{ backgroundColor: '#E8F5E9', color: '#2E7D32' }}>
            <th style={cellStyle}>Date</th>
            <th style={cellStyle}>Day</th>
            <th style={cellStyle}>Event</th>
          </tr>
        </thead>
        <tbody>
          {holidays.map((holiday, index) => (
            <tr key={index}>
              <td style={cellStyle}>{holiday.date}</td>
              <td style={cellStyle}>{holiday.day}</td>
              <td style={cellStyle}>{holiday.event}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <h3>Festivals on Weekends</h3>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr style={{ backgroundColor: '#E8F5E9', color: '#2E7D32' }}>
            <th style={cellStyle}>Date</th>
            <th style={cellStyle}>Day</th>
            <th style={cellStyle}>Event</th>
          </tr>
        </thead>
        <tbody>
          {weekendFestivals.map((festival, index) => (
            <tr key={index}>
              <td style={cellStyle}>{festival.date}</td>
              <td style={cellStyle}>{festival.day}</td>
              <td style={cellStyle}>{festival.event}</td>
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

export default HolidayList;