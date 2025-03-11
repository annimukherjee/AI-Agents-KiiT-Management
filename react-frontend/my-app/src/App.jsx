import { useState } from 'react';
import { BrowserRouter, Routes, Route, NavLink } from "react-router-dom";
import { Sidebar, Menu, MenuItem, SubMenu } from 'react-pro-sidebar';
import Bonafide from "./elements/bonafide";
import Two from "./elements/noc";
import Chatbot from "./elements/chatbot";
import ScholarshipProcessor from './elements/scholarship';  
import RankProcessor from './elements/rank';
import AcademicCalendar from './elements/academic_calender';
import HolidayList from './elements/holidays';
import ExamSchedule from './elements/exams';
// Custom MenuItem component to work with react-router
const CustomMenuItem = ({ to, children }) => {
    return (
        <MenuItem
            component={<NavLink to={to} className={({ isActive }) => isActive ? "active" : ""} />}
        >
            {children}
        </MenuItem>
    );
};

export default function MyApp() {
    const [collapsed, setCollapsed] = useState(false);

    return (
        <BrowserRouter>
            <div style={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>
                {/* Header */}
                <div style={{ 
                    position: 'fixed', 
                    top: 0, 
                    left: 0, 
                    right: 0, 
                    backgroundColor: '#4CAF50',
                    color: 'white',
                    padding: '15px 20px',
                    textAlign: 'center',
                    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                    zIndex: 1000
                }}>
                    <h1 style={{ margin: 0, fontSize: '1.5rem', textShadow: '1px 1px 2px rgba(0,0,0,0.2)' }}>KALINGA INSTITUTE OF INDUSTRIAL TECHNOLOGY</h1>
                </div>

                {/* Sidebar with Material UI styling */}
                <div style={{ marginTop: '60px' }}>
                    <Sidebar 
                        collapsed={collapsed}
                        width="270px"
                        style={{ 
                            height: 'calc(100vh - 60px)',
                            boxShadow: '2px 0 5px rgba(0,0,0,0.1)'
                        }}
                    >
                        <Menu
                            menuItemStyles={{
                                button: {
                                    padding: '10px 15px',
                                    borderRadius: '4px',
                                    margin: '2px 0',
                                    '&:hover': {
                                        backgroundColor: '#f0f0f0',
                                    },
                                    '&.active': {
                                        backgroundColor: '#E8F5E9', // Light green background
                                        color: '#2E7D32', // Darker green text
                                        fontWeight: 'bold'
                                    },
                                },
                                subMenuContent: {
                                    backgroundColor: '#f8f9fa',
                                },
                            }}
                        >
                            <div style={{ padding: '10px 15px', marginBottom: '10px', borderBottom: '1px solid #eee' }}>
                                <p style={{ fontWeight: 'bold', color: '#2E7D32' }}>Management System</p>
                            </div>

                            {/* Toggle sidebar button */}
                            <div style={{ padding: '0 15px 15px 15px' }}>
                                <button 
                                    onClick={() => setCollapsed(!collapsed)} 
                                    style={{
                                        padding: '8px 12px',
                                        backgroundColor: '#E8F5E9',
                                        color: '#2E7D32',
                                        border: 'none',
                                        borderRadius: '4px',
                                        cursor: 'pointer',
                                        width: '100%'
                                    }}
                                >
                                    {collapsed ? 'Expand' : 'Collapse'} Menu
                                </button>
                            </div>

                            {/* SECTION 1: CERTIFICATE GENERATION */}
                            <SubMenu label="CERTIFICATE GENERATION" style={{ fontWeight: 'bold', color: '#2E7D32' }}>
                                <CustomMenuItem to="/noc-generation">NOC Generation</CustomMenuItem>
                                <CustomMenuItem to="/bonafide">Bonafide Certificate</CustomMenuItem>
                                <CustomMenuItem to="/rank-certificate">Rank Certificate</CustomMenuItem>
                                <CustomMenuItem to="/scholarship-certificate">Scholarship Certificate</CustomMenuItem>
                            </SubMenu>

                            {/* SECTION 2: EVENTS & PLACEMENTS */}
                            <SubMenu label="EVENTS & PLACEMENTS" style={{ fontWeight: 'bold', color: '#2E7D32' }}>
                                <CustomMenuItem to="/kiit-events">KIIT Events</CustomMenuItem>
                                <CustomMenuItem to="/career-placements">Career & Placements</CustomMenuItem>
                            </SubMenu>

                            {/* SECTION 3: TUTOR-MENTOR AUTOMATION */}
                            <SubMenu label="TUTOR-MENTOR AUTOMATION" style={{ fontWeight: 'bold', color: '#2E7D32' }}>
                                <CustomMenuItem to="/leave-certificate">Leave Certificate</CustomMenuItem>
                                <CustomMenuItem to="/google-meet">Google Meet Scheduling</CustomMenuItem>
                            </SubMenu>

                            {/* SECTION 4: ACADEMIC ACTIVITIES */}
                            <SubMenu label="ACADEMIC ACTIVITIES" style={{ fontWeight: 'bold', color: '#2E7D32' }}>
                                <CustomMenuItem to="/academic-calendar">Academic Calendar</CustomMenuItem>
                                <CustomMenuItem to="/exam-schedule">Examination Schedule</CustomMenuItem>
                                <CustomMenuItem to="/holiday-list">Holiday List</CustomMenuItem>
                                <CustomMenuItem to="/backlog-queries">Backlog Examination Queries</CustomMenuItem>
                            </SubMenu>

                            {/* SECTION 5: COMPLIANCE CELL */}
                            <SubMenu label="COMPLIANCE CELL" style={{ fontWeight: 'bold', color: '#2E7D32' }}>
                                <CustomMenuItem to="/notices">Important Notices & Policies</CustomMenuItem>
                                <CustomMenuItem to="/grievance">Student Grievance Submission</CustomMenuItem>
                            </SubMenu>

                            {/* SECTION 6: TRAINING & PLACEMENT */}
                            <SubMenu label="TRAINING & PLACEMENT" style={{ fontWeight: 'bold', color: '#2E7D32' }}>
                                <CustomMenuItem to="/placement-drives">Upcoming Placement Drives</CustomMenuItem>
                                <CustomMenuItem to="/company-shortlists">Company Shortlists</CustomMenuItem>
                                <CustomMenuItem to="/interview-guidance">Resume & Interview Guidance</CustomMenuItem>
                            </SubMenu>

                            {/* SECTION 7: AI-BASED QUERY SYSTEM */}
                            <SubMenu label="AI QUERY SYSTEM" style={{ fontWeight: 'bold', color: '#2E7D32' }}>
                            <CustomMenuItem to="/ai-chatbot">AI Chatbot</CustomMenuItem>
                            </SubMenu>
                        </Menu>
                    </Sidebar>
                </div>

                {/* Main Content */}
                <div style={{ 
                    flex: 1, 
                    padding: '20px', 
                    marginTop: '60px',
                    marginLeft: collapsed ? '80px' : '270px',
                    transition: 'margin-left 0.3s',
                    backgroundColor: '#F9FFF9', // Very light green background
                    height: 'calc(100vh - 60px)',
                    overflow: 'auto'
                }}>
                    <Routes>
                        <Route path="/" element={
                            <div style={{
                                textAlign: 'center',
                                margin: '40px auto',
                                backgroundColor: 'white',
                                padding: '30px',
                                borderRadius: '8px',
                                boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                                maxWidth: '800px'
                            }}>
                                <h1 style={{ color: '#2E7D32' }}>Welcome to KIIT Management System</h1>
                                <p>Please select an option from the sidebar to begin.</p>
                            </div>
                        } />
                        <Route path="/bonafide" element={<Bonafide />} />
                        <Route path="/noc-generation" element={<Two />} />
                        <Route path="/rank-certificate" element={<RankProcessor />} />
                        <Route path="/scholarship-certificate" element={<ScholarshipProcessor/>} />
                        <Route path="/kiit-events" element={<Two />} />
                        <Route path="/career-placements" element={<Two />} />
                        <Route path="/leave-certificate" element={<Two />} />
                        <Route path="/google-meet" element={<Two />} />
                        <Route path="/academic-calendar" element={<AcademicCalendar />} />
                        <Route path="/exam-schedule" element={<ExamSchedule />} />
                        <Route path="/holiday-list" element={<HolidayList />} />
                        <Route path="/backlog-queries" element={<Two />} />
                        <Route path="/notices" element={<Two />} />
                        <Route path="/grievance" element={<Two />} />
                        <Route path="/placement-drives" element={<Two />} />
                        <Route path="/company-shortlists" element={<Two />} />
                        <Route path="/interview-guidance" element={<Two />} />
                        <Route path="/ai-chatbot" element={<Chatbot />} />
                    </Routes>
                </div>
            </div>
        </BrowserRouter>
    );
}