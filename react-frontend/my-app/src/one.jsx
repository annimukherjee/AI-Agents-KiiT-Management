import { useState } from 'react';

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
        <div className="form-actions">
            <button 
                className="button" 
                onClick={verifyBonafide} 
                disabled={isLoading}
                style={{ backgroundColor: "#4CAF50" }} // Light green
            >
                {isLoading ? 'Processing...' : 'Verify Bonafide Email'}
            </button>
            {result && (
                <div className="result-message" style={{
                    marginTop: '15px',
                    padding: '10px',
                    backgroundColor: result.includes('Error') ? '#ffebee' : '#E8F5E9', // Light green for success
                    borderRadius: '4px',
                    color: result.includes('Error') ? '#c62828' : '#2E7D32' // Darker green for success
                }}>
                    {result}
                </div>
            )}
        </div>
    );
}

function Bonafide() {
    const [formData, setFormData] = useState({
        studentName: '',
        rollNumber: '',
        program: '',
        batch: '',
        purpose: ''
    });

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        console.log('Form submitted:', formData);
        // Here you would typically send the data to your backend
    };

    return (
        <div className="material-card">
            <h2 style={{ color: "#2E7D32" }}>Bonafide Certificate Generation</h2>
            <p>Fill out the form below to generate a bonafide certificate.</p>

            <form onSubmit={handleSubmit}>
                <div className="form-control">
                    <label htmlFor="studentName">Student Name</label>
                    <input
                        type="text"
                        id="studentName"
                        name="studentName"
                        value={formData.studentName}
                        onChange={handleChange}
                        required
                    />
                </div>

                <div className="form-control">
                    <label htmlFor="rollNumber">Roll Number</label>
                    <input
                        type="text"
                        id="rollNumber"
                        name="rollNumber"
                        value={formData.rollNumber}
                        onChange={handleChange}
                        required
                    />
                </div>

                <div className="form-control">
                    <label htmlFor="program">Program</label>
                    <select
                        id="program"
                        name="program"
                        value={formData.program}
                        onChange={handleChange}
                        required
                    >
                        <option value="">Select Program</option>
                        <option value="B.Tech">B.Tech</option>
                        <option value="M.Tech">M.Tech</option>
                        <option value="BBA">BBA</option>
                        <option value="MBA">MBA</option>
                        <option value="Other">Other</option>
                    </select>
                </div>

                <div className="form-control">
                    <label htmlFor="batch">Batch</label>
                    <input
                        type="text"
                        id="batch"
                        name="batch"
                        placeholder="e.g., 2020-2024"
                        value={formData.batch}
                        onChange={handleChange}
                        required
                    />
                </div>

                <div className="form-control">
                    <label htmlFor="purpose">Purpose of Certificate</label>
                    <textarea
                        id="purpose"
                        name="purpose"
                        rows="3"
                        value={formData.purpose}
                        onChange={handleChange}
                        required
                    ></textarea>
                </div>

                <div style={{ display: 'flex', gap: '10px', marginTop: '20px' }}>
                    <button type="submit" className="button" style={{ backgroundColor: "#4CAF50" }}>Generate Certificate</button>
                    <button type="button" className="button secondary" style={{ color: "#4CAF50", borderColor: "#4CAF50" }}>Cancel</button>
                </div>
            </form>

            <div style={{ marginTop: '30px', borderTop: '1px solid #E8F5E9', paddingTop: '20px' }}>
                <h3 style={{ color: "#2E7D32" }}>Verify Existing Certificate</h3>
                <VerificationButton />
            </div>
        </div>
    );
}

export { Bonafide };
export default Bonafide;