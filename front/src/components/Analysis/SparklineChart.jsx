import React from 'react';
import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Filler } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Filler);

const SparklineChart = ({ data }) => {
  // Set chart color to blue as requested
  const chartColor = '#3a80e9'; 
  
  const chartData = {
    labels: data.map(item => new Date(item[0]).toLocaleDateString()),
    datasets: [{
      data: data.map(item => item[1]),
      borderColor: chartColor,
      backgroundColor: (context) => {
        const ctx = context.chart.ctx;
        const gradient = ctx.createLinearGradient(0, 0, 0, 150);
        gradient.addColorStop(0, `${chartColor}40`); // 25% opacity
        gradient.addColorStop(1, `${chartColor}00`); // 0% opacity
        return gradient;
      },
      tension: 0.25,
      fill: true,
      pointRadius: 0,
    }],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        enabled: false,
      },
    },
    scales: {
      x: {
        display: false,
        grid: {
            display: false,
        }
      },
      y: {
        display: false,
        grid: {
            display: false,
        }
      },
    },
  };

  return <Line data={chartData} options={options} />;
};

export default SparklineChart;
