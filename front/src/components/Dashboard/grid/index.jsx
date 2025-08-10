import React from 'react';
import TrendingUpRoundedIcon from '@mui/icons-material/TrendingUpRounded';
import TrendingDownRoundedIcon from '@mui/icons-material/TrendingDownRounded';
import {motion} from 'framer-motion';
import { Link } from 'react-router-dom';
import StarBorderRoundedIcon from '@mui/icons-material/StarBorderRounded';


function Grid({ coin, delay }) {
  return (
    <Link to={`/coin/${coin.id}`}>
    <motion.div initial={{opacity: 0, y: 100}} animate={{opacity: 1, y: 0}} transition={{duration: 0.5, delay: delay}}
    className={`w-[300px] border-2 border-solid border-darkgrey bg-darkgrey h-[310p] rounded-xl px-6 py-6 
                    ${coin.price_change_percentage_24h > 0 
                    ? 'hover:border-green hover:border-2 hover:border-solid transition-all duration-300'
                    : 'hover:border-red hover:border-2 hover:border-solid transition-all duration-300'}`}>
        <div className='flex flex-row justify-between items-center '>
            <div className='flex flex-row gap-4 justify-start items-center'>
                <img src={coin.image} className='w-14 h-14 object-cover' />
                <div className='flex flex-col gap-1'>
                    <p className='text-white text-xl uppercase font-semibold '>{coin.symbol}</p>
                    <p className= 'text-grey capitalize font-light text-base'>{coin.name}</p>
                </div>
            </div>
            <div className={`border-2 rounded-full float-end p-2 
                            ${coin.price_change_percentage_24h > 0 
                            ? 'text-green border-green'
                            : 'text-red border-red'}`}>
                <StarBorderRoundedIcon />
            </div>
        </div>
        <div className='flex justify-start gap-4 items-center my-5 '>
            <div className={`border-solid border-2 rounded-3xl px-5 py-1 text-center font-semibold text-base transition-all duration-300 
                             ${coin.price_change_percentage_24h > 0 
                             ? 'text-green hover:text-white hover:bg-green  border-green' 
                             : ' text-red hover:text-black hover:bg-red border-red' }`}>
                  {coin.price_change_percentage_24h}%
            </div>
            <div className={`rounded-3xl border-2 border-solid h-8 w-8 items-center flex justify-center transition-all duration-300
                            ${coin.price_change_percentage_24h > 0 
                            ? 'text-green hover:text-white hover:bg-green  border-green' 
                            : ' text-red hover:text-black hover:bg-red border-red' }`}>
                {coin.price_change_percentage_24h > 0 ? <TrendingUpRoundedIcon /> : <TrendingDownRoundedIcon />}
            </div>
        </div>
        <div className='m-1 text-[1.2rem] font-semibold'>
            <h3 className={`${coin.price_change_percentage_24h > 0 ? 'text-green' : 'text-red'}`} >
                ${coin.current_price.toLocaleString()}
            </h3>
            <div className='text-[0.9rem] font-medium mt-3 text-grey'>
                <p className='py-[0.2rem]'>Total Volume : {coin.total_volume.toLocaleString()}</p>
                <p className='py-[0.2rem]'>Market Cap : ${coin.market_cap.toLocaleString()}</p>
            </div>
        </div>
    </motion.div>
    </Link>
  )
}

export default Grid
