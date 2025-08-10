import React from 'react';
import {useState} from 'react';
import ToggleButton from '@mui/material/ToggleButton';
import ToggleButtonGroup from '@mui/material/ToggleButtonGroup';

export default function PriceType({price, handlePrice}) {


  return (
    <div className='flex items-center justify-center m-4 bg-darkgrey'>
        <ToggleButtonGroup
        value={price}
        exclusive
        onChange={handlePrice}
        sx={{
            "& .Mui-selected": {
              color: "#3a80e9 !important",
            },
            borderColor: "#3a80e9",
            border: "unset !important",
            "& .MuiToggleButtonGroup-grouped": {
              border: "1px solid !important",
              borderColor: "unset",
              color: "#3a80e9",
            },
            "& .MuiToggleButton-standard": {
              color: "#3a80e9",
            },
        }}
        >
        <ToggleButton value="prices">Price</ToggleButton>
        <ToggleButton value="total_volumes">Volume</ToggleButton>
        </ToggleButtonGroup>
    </div>
  );
}
