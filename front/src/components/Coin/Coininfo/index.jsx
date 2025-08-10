import React, { useState } from 'react';
import './styles.css';
import { motion } from 'framer-motion';

function CoinInfo({heading, desc, delay, descriptionClass}) {
    const shortDesc = desc ? desc.slice(0, 350) + "<p id='special' className=' text-grey'> Read More...</p>" : "";
    const longDesc = desc ? desc + "<p id='special' className=' text-grey'> Read Less...</p>" : "";

    const [flag, setFlag] = useState(false);

  return (
    <motion.div className='bg-darkgrey p-5'
    initial={{opacity: 0, y: 100}} animate={{opacity: 1, y: 0}} transition={{duration: 0.5, delay: delay}}>
        <h1 className='font-bold text-[2rem]'>{heading}</h1>
        {desc.length > 350 ?
        <p className={`text-blue`}
        onClick={()=>{
            setFlag(!flag);
        }}
        dangerouslySetInnerHTML={{__html: !flag ? shortDesc : longDesc} } />
        : <p className={`text-blue`} dangerouslySetInnerHTML={{__html: !flag ? shortDesc : longDesc} } />}
    </motion.div>
  )
}

export default CoinInfo;