import React from 'react';
import {Line} from 'react-chartjs-2';
import {Chart as ChartJS} from 'chart.js/auto';
import { convertNums } from '../../../functions/ConvertNums';

function LineChart({chartData, priceType, multiAxis}) {
    if (!chartData || !chartData.labels) {
        return <div className='flex justify-center items-center h-[400px]'>No chart data available</div>;
    }

    const options = {
        plugins: {
            legend: {
                display: multiAxis ? true : false,
            },
        },
        responsive: true,
        interaction: {
            mode: 'index',
            intersect: false,
        },
        scales: {
            crypto1: {
                type: 'linear',
                display: true,
                position: 'left',
                ticks:{
                    callback: function(value, index, ticks) {
                        if (priceType === "total_volumes" || priceType === "market_caps") {
                            return "$" + convertNums(value);
                        }
                        return "$" + value;
                    }
                },
            },
            crypto2: {
                type: 'linear',
                display: true,
                position: 'right',
                ticks:{
                    callback: function(value, index, ticks) {
                        if (priceType === "total_volumes" || priceType === "market_caps") {
                            return "$" + convertNums(value);
                        }
                        return "$" + value;
                    }
                },
            },
        },
    }

    return (
        <div className='flex justify-center max-h-[575px] bg-darkgrey'>
            <Line data={chartData} options={options} />
        </div>
    )
}

export default LineChart;