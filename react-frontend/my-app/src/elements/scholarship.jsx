import { useState } from 'react';

function ScholarshipProcessor() {
    const [isLoading, setIsLoading] = useState(false);
    const [isSending, setIsSending] = useState(false);
    const [requests, setRequests] = useState([]);
    const [message, setMessage] = useState(null);

    const fetchScholarshipRequests = async () => {
        setIsLoading(true);
        setMessage(null);

        try {
            const response = await fetch('http://localhost:8000/fetch-scholarship-requests');

            if (!response.ok) {
                throw new Error(`Server responded with status: ${response.status}`);
            }

            const data = await response.json();
            setRequests(data);

            if (data.length === 0) {
                setMessage({
                    text: 'No scholarship requests found in inbox',
                    isError: false
                });
            } else {
                setMessage({
                    text: `Found ${data.length} scholarship requests`,
                    isError: false
                });
            }
        } catch (err) {
            console.error('Error fetching scholarship requests:', err);
            setMessage({
                text: `Error: ${err.message || 'Failed to connect to server'}`,
                isError: true
            });
        } finally {
            setIsLoading(false);
        }
    };

    const sendCertificates = async () => {
        // Only send for verified requests
        const verifiedRequests = requests.filter(request => request.verified);

        if (verifiedRequests.length === 0) {
            setMessage({
                text: 'No verified scholarship requests to process',
                isError: true
            });
            return;
        }

        setIsSending(true);
        setMessage(null);

        try {
            const response = await fetch('http://localhost:8000/send-scholarship-certificates', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ requests: verifiedRequests }),
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
            console.error('Error sending scholarship certificates:', err);
            setMessage({
                text: `Error: ${err.message || 'Failed to connect to server'}`,
                isError: true
            });
        } finally {
            setIsSending(false);
        }
    };

    return (
        <div className="material-card">
            <h2 style={{ color: "#2E7D32" }}>Scholarship Certificate System</h2>
            <p>Process scholarship certificate requests from emails.</p>

            <div className="form-actions" style={{ marginBottom: '20px' }}>
                <button
                    className="button"
                    onClick={fetchScholarshipRequests}
                    disabled={isLoading}
                    style={{
                        backgroundColor: "#2196F3",
                        marginRight: '10px'
                    }}
                >
                    {isLoading ? 'Fetching...' : 'Fetch Scholarship Requests'}
                </button>

                <button
                    className="button"
                    onClick={sendCertificates}
                    disabled={isSending || requests.length === 0}
                    style={{ backgroundColor: "#4CAF50" }}
                >
                    {isSending ? 'Sending...' : 'Send Certificates'}
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

            {requests.length > 0 && (
                <div className="request-table-container">
                    <h3 style={{ color: "#2E7D32" }}>Found Scholarship Requests</h3>
                    <table style={{
                        width: '100%',
                        borderCollapse: 'collapse',
                        marginTop: '10px'
                    }}>
                        <thead>
                            <tr style={{
                                backgroundColor: '#E8F5E9',
                                color: '#2E7D32'
                            }}>
                                <th style={cellStyle}>Name</th>
                                <th style={cellStyle}>Roll Number</th>
                                <th style={cellStyle}>Email</th>
                                <th style={cellStyle}>Email Content</th>
                                <th style={cellStyle}>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {requests.map((request, index) => (
                                <tr key={index}>
                                    <td style={cellStyle}>{request.name}</td>
                                    <td style={cellStyle}>{request.rollnum}</td>
                                    <td style={cellStyle}>{request.email}</td>
                                    <td style={cellStyle}>
                                        <div style={{
                                            maxHeight: '80px',
                                            overflow: 'auto',
                                            fontSize: '0.9em',
                                            color: '#666'
                                        }}>
                                            {request.email_text}
                                        </div>
                                    </td>
                                    <td style={cellStyle}>
                                        {request.verified ? (
                                            <span style={{
                                                color: '#4CAF50',
                                                fontWeight: 'bold',
                                                backgroundColor: '#E8F5E9',
                                                padding: '3px 8px',
                                                borderRadius: '12px',
                                                fontSize: '0.85em'
                                            }}>
                                                Verified
                                            </span>
                                        ) : (
                                            <span style={{
                                                color: '#F44336',
                                                fontWeight: 'bold',
                                                backgroundColor: '#FFEBEE',
                                                padding: '3px 8px',
                                                borderRadius: '12px',
                                                fontSize: '0.85em'
                                            }}>
                                                Not Verified
                                            </span>
                                        )}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
}

const cellStyle = {
    padding: '10px',
    borderBottom: '1px solid #e0e0e0',
    textAlign: 'left'
};

export { ScholarshipProcessor };
export default ScholarshipProcessor;
