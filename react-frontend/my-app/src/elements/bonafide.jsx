import { useState } from 'react';

function BonafideProcessor() {
    const [isLoading, setIsLoading] = useState(false);
    const [isSending, setIsSending] = useState(false);
    const [students, setStudents] = useState([]);
    const [selectedStudents, setSelectedStudents] = useState({});
    const [message, setMessage] = useState(null);

    const fetchBonafideRequests = async () => {
        setIsLoading(true);
        setMessage(null);
        setSelectedStudents({});

        try {
            const response = await fetch('http://localhost:8000/fetch-bonafide-requests');

            if (!response.ok) {
                throw new Error(`Server responded with status: ${response.status}`);
            }

            const data = await response.json();
            setStudents(data);

            // Initialize selected state for all students (default to false)
            const initialSelection = {};
            data.forEach(student => {
                initialSelection[student.rollnum] = false;
            });
            setSelectedStudents(initialSelection);

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

    const handleSelectStudent = (rollnum) => {
        setSelectedStudents(prev => ({
            ...prev,
            [rollnum]: !prev[rollnum]
        }));
    };

    const handleSelectAll = (checked) => {
        const updatedSelection = {};
        students.forEach(student => {
            updatedSelection[student.rollnum] = checked;
        });
        setSelectedStudents(updatedSelection);
    };

    const sendCertificates = async () => {
        // Filter students based on selection and verification
        const studentsToSend = students.filter(
            student => selectedStudents[student.rollnum] && student.verified
        );

        if (studentsToSend.length === 0) {
            setMessage({
                text: 'No verified students selected to process',
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
                body: JSON.stringify({ students: studentsToSend }),
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

    // Count selected verified students
    const selectedVerifiedCount = students.filter(
        student => selectedStudents[student.rollnum] && student.verified
    ).length;

    // Count selected total students
    const selectedCount = Object.values(selectedStudents).filter(Boolean).length;

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
                    disabled={isSending || selectedVerifiedCount === 0}
                    style={{ backgroundColor: "#4CAF50" }} // Green
                >
                    {isSending ? 'Sending...' : `Send Certificates (${selectedVerifiedCount})`}
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
                    <div style={{ marginBottom: '10px' }}>
                        <label style={{ display: 'flex', alignItems: 'center', fontSize: '0.9em', color: '#555' }}>
                            <input
                                type="checkbox"
                                checked={selectedCount === students.length}
                                onChange={(e) => handleSelectAll(e.target.checked)}
                                style={{ marginRight: '5px' }}
                            />
                            Select All ({selectedCount}/{students.length} selected)
                        </label>
                    </div>
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
                            <th style={cellStyle}>Select</th>
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
                                <td style={cellStyle}>
                                    <input
                                        type="checkbox"
                                        checked={!!selectedStudents[student.rollnum]}
                                        onChange={() => handleSelectStudent(student.rollnum)}
                                        disabled={!student.verified}
                                        style={{ cursor: student.verified ? 'pointer' : 'not-allowed' }}
                                    />
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