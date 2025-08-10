import React from 'react';
import MenuItem from '@mui/material/MenuItem';
import Select from '@mui/material/Select';

export default function DropDown({days, handleDaysChange}) {

  const menuProps = {
    PaperProps: {
      sx: {
        bgcolor: 'rgba(50, 50, 50, 0.9)', // Dark grey background with opacity
        color: 'white', // White text color
        '& .MuiMenuItem-root': {
          '&:hover': {
            bgcolor: 'rgba(70, 70, 70, 0.9)', // Slightly lighter grey on hover
          },
        },
      },
    },
  };

  return (
        <Select
            sx={{
                height: '2.5rem',
                color: 'var(--white)', // Text color for the select box
                "& .MuiOutlinedInput-notchedOutline": {
                borderColor: "var(--white)", // Border color
                },
            }}
            MenuProps={menuProps} 
            labelId="demo-simple-select-label"
            id="demo-simple-select"
            value={days}
            label="Time"
            onChange={handleDaysChange}
        >
          <MenuItem value={7}>7 Days</MenuItem>
          <MenuItem value={30}>30 Days</MenuItem>
          <MenuItem value={60}>60 Days</MenuItem>
          <MenuItem value={90}>90 Days</MenuItem>
          <MenuItem value={120}>120 Days</MenuItem>
          <MenuItem value={365}>1 Year</MenuItem>
        </Select>
  );
}
