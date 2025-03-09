import { useState } from 'react';
import { Sidebar, Menu, MenuItem, SubMenu } from 'react-pro-sidebar';
import {Link} from "react-router-dom";
import One from "./one";
import Two from "./two";

function VerificationButton() {
    const [isLoading, setIsLoading] = useState(false);
    const [result, setResult] = useState(null);

    const verifyBonafide = async () => {
        setIsLoading(true);

        try {
            const response = await fetch('http://localhost:8000/verify-bonafide');
            const data = await response.json();
            setResult(data.message);
        } catch (err) {
            setResult('Error connecting to server');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div>
            <button onClick={verifyBonafide} disabled={isLoading}>
                {isLoading ? 'Processing...' : 'Verify Bonafide Email'}
            </button>
            {result && <p>{result}</p>}
        </div>
    );
}

export default function MyApp() {
    return (
        <div style={{ display: 'flex', height: '100vh' }}>
            {/* Sidebar */}
            <Sidebar>
                <Menu>
                    <SubMenu label="Navigation">
                        <MenuItem>Student</MenuItem>
                        <MenuItem>Guy</MenuItem>
                    </SubMenu>
                    <MenuItem>Bonafide generation</MenuItem>
                    <MenuItem>some sort of generation</MenuItem>
                </Menu>
            </Sidebar>

            {/* Main Content */}
            <div style={{ flex: 1, padding: '20px' }}>
                <h1>Bonafide generation</h1>
                <VerificationButton />
            </div>
        </div>
    );
}
