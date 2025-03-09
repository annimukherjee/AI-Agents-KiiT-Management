import { useState, useEffect } from 'react';

function Sidebar() {
    const [isSticky, setIsSticky] = useState(false);

    useEffect(() => {
        const handleScroll = () => {
            if (window.scrollY > 100) {
                setIsSticky(true);
            } else {
                setIsSticky(false);
            }
        };

        window.addEventListener('scroll', handleScroll);

        // Clean up
        return () => {
            window.removeEventListener('scroll', handleScroll);
        };
    }, []);

    return (
        <div className={`sidebar ${isSticky ? 'sticky' : ''}`}>
            <h3>Quick Links</h3>
            <ul>
                <li><a href="#">Home</a></li>
                <li><a href="#">Verify Bonafide</a></li>
                <li><a href="#">Student Records</a></li>
                <li><a href="#">Settings</a></li>
                <li><a href="#">Help</a></li>
            </ul>
        </div>
    );
}

export default Sidebar;