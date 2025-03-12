import { useState } from 'react';

function ScholarshipProcessor() {
    const [isProcessing, setIsProcessing] = useState(false);
    const [message, setMessage] = useState(null);

    const processScholarshipRequests = async () => {
        setIsProcessing(true);
        setMessage(null);

        try {
            // Call the process endpoint (GET or POST as per backend; here GET is used)
            const response = await fetch('http://localhost:8000/scholarship/process', {
                method: 'GET'
            });

            if (!response.ok) {
                throw new Error(`Server responded with status: ${response.status}`);
            }

            const result = await response.json();
            setMessage({
                text: result.message,
                isError: false
            });
        } catch (err) {
            console.error('Error processing scholarship requests:', err);
            setMessage({
                text: `Error: ${err.message || 'Failed to connect to server'}`,
                isError: true
            });
        } finally {
            setIsProcessing(false);
        }
    };

    return (
        <div className="material-card">
            <h2 style={{ color: "#2E7D32" }}>Scholarship Certificate System</h2>
            <p>Process scholarship certificate requests from emails.</p>

            <div className="form-actions" style={{ marginBottom: '20px' }}>
                <button
                    className="button"
                    onClick={processScholarshipRequests}
                    disabled={isProcessing}
                    style={{
                        backgroundColor: "#2196F3",
                        marginRight: '10px'
                    }}
                >
                    {isProcessing ? 'Processing...' : 'Process Scholarship Requests'}
                </button>
            </div>

            {message && (
                <div className="result-message" style={{
                    marginBottom: '20px',
                    padding: '10px',
                    backgroundColor: message.isError ? '#ffebee' : '#E8F5E9',
                    borderRadius: '4px',
                    color: message.isError ? '#c62828' : '#2E7D32'
                }}>
                    {message.text}
                </div>
            )}
        </div>
    );
}

export { ScholarshipProcessor };
export default ScholarshipProcessor;
