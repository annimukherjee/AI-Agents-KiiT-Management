import { useState } from 'react';
import { Sidebar, Menu, MenuItem } from 'react-pro-sidebar';
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import Bonafide from "./one";
import Two from "./two";

export default function MyApp() {
    return (
        <BrowserRouter>
            <div style={{ display: 'flex', height: '100vh' }}>
                <Sidebar>
                    <Menu
                        menuItemStyles={{
                            button: {
                                // the active class will be added automatically by react router
                                // so we can use it to style the active menu item
                                [`&.active`]: {
                                    backgroundColor: '#13395e',
                                    color: '#b6c8d9',
                                },
                            },
                        }}
                    >
                        <MenuItem component={<Link to="/bonafide" />}>Bonafide generation</MenuItem>
                        <MenuItem component={<Link to="/some-generation" />}>Some sort of generation</MenuItem>
                    </Menu>
                </Sidebar>

                {/* Main Content */}
                <div style={{ flex: 1, padding: '20px' }}>
                    <Routes>
                        <Route path="/" element={<h1>Welcome to the Management Dashboard!</h1>} />
                        <Route path="/bonafide" element={<Bonafide />} />
                        <Route path="/some-generation" element={<Two />} />
                    </Routes>
                </div>
            </div>
        </BrowserRouter>
    );
}