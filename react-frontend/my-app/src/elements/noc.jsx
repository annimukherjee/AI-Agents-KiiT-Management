import { useState } from "react";

export default function Two() {
    const [response, setResponse] = useState("");

    const callBackend = async () => {
        try {
            const res = await fetch("http://localhost:8000/noc/generatenoc");
            const data = await res.json();
            setResponse(data.message);
        } catch (error) {
            setResponse("Error calling backend");
        }
    };

    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100">
            <button
                onClick={callBackend}
                className="px-4 py-2 text-white bg-blue-500 rounded hover:bg-blue-600"
            >
                Call Backend
            </button>
            {response && <p className="mt-4 text-lg">{response}</p>}
        </div>
    );
}
