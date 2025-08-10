import React from 'react'
import './styles.css';
import SearchRoundedIcon from '@mui/icons-material/SearchRounded';

function Search({search, onSearchChange}) {
    return (
    <div className='bg-darkgrey text-grey flex items-center gap-[1.5rem] px-[3rem] py-[1rem] 
                    justify-start w-[80%] mr-auto ml-auto m-[1rem] rounded-[3rem]'>
        <SearchRoundedIcon className='text-white' />
        <input className="bg-darkgrey w-[100%] font-['Inter'] text-[0.9rem] text-grey border-none
                          focus:outline-none "
                placeholder='Search' 
                type='text' 
                value={search} 
                onChange={(e) => onSearchChange(e)}/>
    </div>
  )
}

export default Search