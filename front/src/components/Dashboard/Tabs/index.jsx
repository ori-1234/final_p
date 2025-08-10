import React from 'react';
import './styles.css';
import Tab from '@mui/material/Tab';
import TabContext from '@mui/lab/TabContext';
import TabList from '@mui/lab/TabList';
import TabPanel from '@mui/lab/TabPanel';
import Grid from '../grid';
import List from '../List';
import { motion } from 'framer-motion';
import { ThemeProvider, createTheme } from '@mui/material/styles';

export default function TabsCompnent({ coins }) {
  const [value, setValue] = React.useState('grid');

  const handleChange = (event, newValue) => {
    setValue(newValue);
  };

  const theme = createTheme({
    palette: {
        primary: {
            main: "#3a80e9",
        }
    },
  })

  const style = {
    color: '#fff',
    width: '50vw',
    fontSize: '1.2rem',
    fontWeight: 600,
    fontFamily: 'Inter',
    textTransform: 'capitalize',
  }

  return (
    <ThemeProvider theme={theme}>
      <TabContext value={value}>
          <TabList onChange={handleChange} variant='fullWidth'>
            <Tab label="Grid" value="grid" sx={style}/>
            <Tab label="List" value="list" sx={style}/>
          </TabList>
        <TabPanel value="grid">
            <div className='flex justify-center items-center flex-wrap gap-4 mx-8 my-6'>
            {coins.map((coin, i) => {
                return (
                  
                    <Grid coin={coin} key={i} delay={(i % 4) * 0.2} />
                
                );})}
            </div>

        </TabPanel>
        <TabPanel value="list">
          <table className='table-style w-[85%] sm:w-[95%]  block ml-auto mr-auto'>
            {coins.map((coin, i) => {
              return(
                    <List color={'black'} coin={coin} key={i} delay={(i % 8) * 0.2}/>
                );})}
          </table>
        </TabPanel>
      </TabContext>
    </ThemeProvider>
  );
}
