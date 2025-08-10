import React from 'react'
import CircularProgress from '@mui/material/CircularProgress';
//import 'styles.css';

function Loader() {
  return (
    <div className='flex justify-center items-center w-full h-full bg-black text-blue absolute z-[1000]'>
      <CircularProgress />
    </div>
  );
}

export default Loader;