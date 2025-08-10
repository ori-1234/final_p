import React from 'react';
import './styles.css';

function Button({label, onClick, outLined}) {
  return (
  <div className = {outLined ? 'outlined-btn' : 'btn'}
    onClick={() => onClick()}>
    {label}
  </div>
  
  );
}

export default Button;