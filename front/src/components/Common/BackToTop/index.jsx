/*
import React from 'react';
import './styles.css';
import ArrowUpwardRoundedIcon from '@mui/icons-material/ArrowUpwardRounded';

function BackToTop() {
    // Get the button:
    const mybutton = document.getElementById("myBtn");

    // When the user scrolls down 20px from the top of the document, show the button
    window.onscroll = () => scrollFunction();

    function scrollFunction() {
    if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
        mybutton.style.display = "flex";
    } else {
        mybutton.style.display = "none";
    }
    }

    // When the user clicks on the button, scroll to the top of the document
    function topFunction() {
        document.body.scrollTop = 0; // For Safari
        document.documentElement.scrollTop = 0; // For Chrome, Firefox, IE and Opera
    }
    return (
        <button onClick={() => topFunction()} id="myBtn" title="Go to top">
            <ArrowUpwardRoundedIcon className='text-blue' />
        </button>
    )
}

export default BackToTop;
*/
import React, { useEffect } from 'react';
import './styles.css';
import ArrowUpwardRoundedIcon from '@mui/icons-material/ArrowUpwardRounded';

function BackToTop() {
    useEffect(() => {
        // Get the button after the component is rendered
        const mybutton = document.getElementById("myBtn");

        if (!mybutton) return; // Ensure the button exists

        // Function to show/hide the button based on scroll position
        const scrollFunction = () => {
            if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
                mybutton.style.display = "flex";
            } else {
                mybutton.style.display = "none";
            }
        };

        // Attach the scroll event listener
        window.addEventListener("scroll", scrollFunction);

        // Cleanup the event listener when the component unmounts
        return () => {
            window.removeEventListener("scroll", scrollFunction);
        };
    }, []); // Empty dependency array to run only on mount

    // Scroll to the top of the document
    const topFunction = () => {
        document.body.scrollTop = 0; // For Safari
        document.documentElement.scrollTop = 0; // For Chrome, Firefox, IE, and Opera
    };

    return (
        <button onClick={topFunction} id="myBtn" title="Go to top" style={{ display: 'none' }}>
            <ArrowUpwardRoundedIcon className='text-blue' />
        </button>
    );
}

export default BackToTop;
