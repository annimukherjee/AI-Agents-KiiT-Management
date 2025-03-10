import { useState } from 'react';
import { Sidebar, Menu, MenuItem, SubMenu } from 'react-pro-sidebar';

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

// Fixed component with proper return structure
function Bonafide() {
    return (
        <div className="bonafide-container">
            {/* Main Content */}
            <div className="content">
                <h1>Bonafide generation</h1>
                <VerificationButton />
            </div>
        </div>
    );
}

// Export as both default and named export for flexibility
export { Bonafide };
export default Bonafide;