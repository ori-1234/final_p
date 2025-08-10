import React, { useEffect } from 'react';
import './styles.css';
import TrendingUpRoundedIcon from '@mui/icons-material/TrendingUpRounded';
import TrendingDownRoundedIcon from '@mui/icons-material/TrendingDownRounded';
import StarBorderRoundedIcon from '@mui/icons-material/StarBorderRounded';
import Tooltip from '@mui/material/Tooltip';
import { convertNums } from '../../../functions/ConvertNums';
import {motion} from 'framer-motion';
import { useNavigate } from 'react-router-dom';

function List({coin, delay, color}) {
    const navigate = useNavigate();
    
    if (!coin || typeof coin !== 'object') {
        return null;
    }

    const handleClick = () => {
        navigate(`/coin/${coin.symbol}`);
    };

    return (
        <motion.div 
            onClick={handleClick}
            initial={{opacity: 0, x: -50}} 
            animate={{opacity: 1, x: 0}} 
            transition={{duration: 0.5, delay: delay}}
            className={`flex flex-row w-full sm:min-w-[10rem] sm:h-full items-center bg-${color} rounded-xl 
                px-6 py-3 transition-all duration-300 hover:bg-darkgrey cursor-pointer`}
        >
            <div className='flex justify-start items-center gap-4 flex-1'>
                <Tooltip title="Coin Logo" placement='bottom-start'>
                    <img src={coin.image} className='coin-logo w-14 h-14 sm:w-10 sm:h-10' alt={coin.name} />
                </Tooltip>
                <Tooltip title="Coin Info" placement='bottom-start'>
                    <div className='flex flex-col gap-1'>
                        <p className='sym text-white text-xl uppercase font-semibold sm:text-base'>{coin.symbol}</p>
                        <p className='name text-grey capitalize font-light text-base sm:text-sm'>{coin.name}</p>
                    </div>
                </Tooltip>
            </div>

            <div className='flex flex-row justify-start items-center gap-[7%] flex-1'>
                <Tooltip title="Price Change In 24h" placement='bottom-start'>
                    <div className={`border-solid border-2 rounded-3xl px-5 py-1 items-center justify-center font-semibold text-base transition-all 
                                    duration-300 flex min-w-[110px] sm:min-w-[98px] sm:text-sm price-change
                                    ${coin.price_change_percentage_24h > 0 
                                    ? 'text-green hover:text-white hover:bg-green border-green' 
                                    : 'text-red hover:text-black hover:bg-red border-red'}`}>
                        {coin.price_change_percentage_24h?.toFixed(2)}%
                    </div>
                </Tooltip>
                <div className={`trend-style rounded-3xl border-solid h-8 w-8 items-center transition-all duration-300
                                ${coin.price_change_percentage_24h > 0 
                                ? 'border-2 text-green hover:text-white hover:bg-green border-green' 
                                : 'border-2 text-red hover:text-black hover:bg-red border-red'}`}>
                    {coin.price_change_percentage_24h > 0 ? <TrendingUpRoundedIcon /> : <TrendingDownRoundedIcon />} 
                </div>
            </div>

            <div className='flex-1'>
                <Tooltip title="Current Price" placement='bottom-start'>
                    <div className='price text-lg font-medium'>
                        <h3 className={`${coin.price_change_percentage_24h > 0 ? 'text-green' : 'text-red'}`}>
                            ${coin.current_price?.toLocaleString()}
                        </h3>
                    </div>
                </Tooltip>
                <Tooltip title="Current Price" placement='bottom-start'>
                    <div className='mobile-price text-lg font-medium'>
                        <h3 className={`${coin.price_change_percentage_24h > 0 ? 'text-green' : 'text-red'}`}>
                            ${coin.current_price ? convertNums(coin.current_price) : '0'} 
                        </h3>
                    </div>
                </Tooltip>
            </div>

            <div className='flex-1'>
                <Tooltip title="Total Volume" placement='bottom-start'>
                    <div className='hidden md:block'>
                        <p className='py-[0.2rem]'>{coin.total_volume?.toLocaleString()}</p>
                    </div>
                </Tooltip>
            </div>

            <div className='flex-1'>
                <Tooltip title="Market Cap" placement='bottom-start'>
                    <div className='market-cap'>
                        <p className='py-[0.2rem]'>${coin.market_cap?.toLocaleString()}</p>
                    </div>
                </Tooltip>
                <Tooltip title="Market Cap" placement='bottom-start'>
                    <div className='mobile-market-cap'>
                        <p className='py-[0.2rem]'>${coin.market_cap ? convertNums(coin.market_cap) : '0'}</p>
                    </div>
                </Tooltip>
            </div>
        </motion.div>
    );
}

export default List;