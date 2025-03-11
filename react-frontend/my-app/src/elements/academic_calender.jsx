import React from 'react';

function AcademicCalendar() {
    const calendarData = [
        { activity: "Spring Academic Session", date: "02nd December 2024 - 22nd April 2025" },
        { activity: "Reporting / Registration / Academic Induction / Sharing of Academic Vision", date: "02nd December 2024 — 3rd December 2024" },
        { activity: "Pre-Mid Semester Session", date: "04th December 2024 — 15th February 2025" },
        { activity: "Mid-Semester Examination", date: "17th February 2025 - 22nd February 2025" },
        { activity: "Post-Mid Semester Session", date: "23rd February 2025 - 11th April 2025" },
        { activity: "End Semester Examination", date: "12th April 2025 - 22nd April 2025" },
        { activity: "Starting of the Next Semester", date: "1st Week of July 2025" },
    ];

    return (
        <div className="calendar-container" style={containerStyle}>
            <h2 style={{ color: "#2E7D32" }}>Academic Calendar - Spring Semester 2024</h2>
            <p>B.Tech (4th / 6th / 8th Semester) - KIIT University</p>
            
            <table style={tableStyle}>
                <thead>
                    <tr style={headerStyle}>
                        <th style={cellStyle}>Activity</th>
                        <th style={cellStyle}>Date</th>
                    </tr>
                </thead>
                <tbody>
                    {calendarData.map((entry, index) => (
                        <tr key={index} style={index % 2 === 0 ? rowEvenStyle : rowOddStyle}>
                            <td style={cellStyle}>{entry.activity}</td>
                            <td style={cellStyle}>{entry.date}</td>
                        </tr>
                    ))}
                </tbody>
            </table>

            <div style={{ marginTop: '20px', color: '#444' }}>
                <p><b>Note:</b> Second and Fourth Saturdays are reserved for Tutor-Mentoring activities.</p>
                <p>Faculty members may use other Saturdays for course-related activities or events.</p>
            </div>
        </div>
    );
}

// Styling
const containerStyle = {
    padding: "20px",
    backgroundColor: "#f5f5f5",
    borderRadius: "10px",
    boxShadow: "0 4px 8px rgba(0, 0, 0, 0.1)",
    maxWidth: "800px",
    margin: "20px auto",
    textAlign: "center",
};

const tableStyle = {
    width: "100%",
    borderCollapse: "collapse",
    marginTop: "10px",
};

const headerStyle = {
    backgroundColor: "#E8F5E9",
    color: "#2E7D32",
};

const rowEvenStyle = {
    backgroundColor: "#FFFFFF",
};

const rowOddStyle = {
    backgroundColor: "#F1F8E9",
};

const cellStyle = {
    padding: "12px",
    borderBottom: "1px solid #e0e0e0",
    textAlign: "left",
};

export default AcademicCalendar;
