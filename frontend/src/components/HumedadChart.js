import React from 'react';
import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, TimeScale, LinearScale, LineElement, PointElement, Title, Tooltip, Legend } from 'chart.js';
import 'chartjs-adapter-date-fns';

ChartJS.register(TimeScale, LinearScale, LineElement, PointElement, Title, Tooltip, Legend);

const HumedadChart = ({ data }) => {
  const chartData = {
    labels: data.humedad.map(point => new Date(point.x)),
    datasets: [
      {
        label: 'Humedad',
        data: data.humedad,
        fill: false,
        backgroundColor: 'blue',
        borderColor: 'blue',
      },
    ],
  };

  const options = {
    scales: {
      x: {
        type: 'time',
        time: {
          parser: 'yyyy-MM-ddTHH:mm:ss.SSSZ',
          unit: 'second',
          displayFormats: {
            second: 'HH:mm:ss',
          },
          tooltipFormat: 'yyyy-MM-dd HH:mm:ss',
        },
        ticks: {
          source: 'data',
          autoSkip: false,
          callback: function(value, index, values) {
            const date = new Date(value);
            return date.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
          },
          maxRotation: 0,
          minRotation: 0,
          sampleSize: 7, // Agregar esta línea para limitar el número de muestras a 7
        },
        title: {
          display: true,
          text: 'Hora',
        },
      },
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Humedad (%)',
        },
      },
    },
    plugins: {
      legend: {
        display: true,
        position: 'top',
      },
    },
  };

  return <Line data={chartData} options={options} />;
};

export default HumedadChart;
