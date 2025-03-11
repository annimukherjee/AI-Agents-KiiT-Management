import { useState } from 'react';

function BonafideProcessor() {
    const [isLoading, setIsLoading] = useState(false);
    const [isSending, setIsSending] = useState(false);
    const [students, setStudents] = useState([]);
    const [message, setMessage] = useState(null);

    const fetchBonafideRequests = async () => {
        setIsLoading(true);
        setMessage(null);

        try {
            const response = await fetch('http://localhost:8000/fetch-bonafide-requests');

            if (!response.ok) {
                throw new Error(`Server responded with status: ${response.status}`);
            }

            const data = await response.json();
            setStudents(data);

            if (data.length === 0) {
                setMessage({
                    text: 'No bonafide requests found in inbox',
                    isError: false
                });
            } else {
                setMessage({
                    text: `Found ${data.length} bonafide requests`,
                    isError: false
                });
            }
        } catch (err) {
            console.error('Error fetching bonafide requests:', err);
            setMessage({
                text: `Error: ${err.message || 'Failed to connect to server'}`,
                isError: true
            });
        } finally {
            setIsLoading(false);
        }
    };

    const sendCertificates = async () => {
        // Only send for verified students
        const verifiedStudents = students.filter(student => student.verified);

        if (verifiedStudents.length === 0) {
            setMessage({
                text: 'No verified students to process',
                isError: true
            });
            return;
        }

        setIsSending(true);
        setMessage(null);

        try {
            const response = await fetch('http://localhost:8000/send-certificates', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ students: verifiedStudents }),
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
            console.error('Error sending certificates:', err);
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
            <h2 style={{ color: "#2E7D32" }}>Bonafide Certificate System</h2>
            <p>Process bonafide certificate requests from emails.</p>

            <div className="form-actions" style={{ marginBottom: '20px' }}>
                <button
                    className="button"
                    onClick={fetchBonafideRequests}
                    disabled={isLoading}
                    style={{
                        backgroundColor: "#2196F3", // Blue
                        marginRight: '10px'
                    }}
                >
                    {isLoading ? 'Fetching...' : 'Fetch Bonafide Requests'}
                </button>

                <button
                    className="button"
                    onClick={sendCertificates}
                    disabled={isSending || students.length === 0}
                    style={{ backgroundColor: "#4CAF50" }} // Green
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

            {students.length > 0 && (
                <div className="student-table-container">
                    <h3 style={{ color: "#2E7D32" }}>Found Requests</h3>
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
                        {students.map((student, index) => (
                            <tr key={index}>
                                <td style={cellStyle}>{student.name}</td>
                                <td style={cellStyle}>{student.rollnum}</td>
                                <td style={cellStyle}>{student.email}</td>
                                <td style={cellStyle}>
                                    <div style={{
                                        maxHeight: '80px',
                                        overflow: 'auto',
                                        fontSize: '0.9em',
                                        color: '#666'
                                    }}>
                                        {student.email_text}
                                    </div>
                                </td>
                                <td style={cellStyle}>
                                    {student.verified ? (
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

// Cell styling for the table
const cellStyle = {
    padding: '10px',
    borderBottom: '1px solid #e0e0e0',
    textAlign: 'left'
};

export { BonafideProcessor };
export default BonafideProcessor;