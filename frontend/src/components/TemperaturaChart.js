import React, { useEffect, useState } from 'react';
import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, TimeScale, LinearScale, LineElement, PointElement, Title, Tooltip, Legend } from 'chart.js';
import 'chartjs-adapter-date-fns';

ChartJS.register(TimeScale, LinearScale, LineElement, PointElement, Title, Tooltip, Legend);

const TemperaturaChart = ({ data }) => {
  const [chartData, setChartData] = useState({ labels: [], datasets: [] });

  useEffect(() => {
    if (data.timestamp.length > 0 && data.ultimas_temperaturas.length > 0) {
      const formattedTimestamps = data.timestamp.map(timestamp => new Date(timestamp));

      setChartData({
        labels: formattedTimestamps,
        datasets: [
          {
            label: 'Temperatura',
            data: data.timestamp.map((timestamp, index) => ({
              x: new Date(timestamp), // Convertir timestamp directamente a Date
              y: data.ultimas_temperaturas[index],
            })),
            fill: false,
            backgroundColor: 'red',
            borderColor: 'red',
          },
        ],
      });
    }
  }, [data]);

  const options = {
    scales: {
      x: {
        type: 'time',
        time: {
          parser: 'yyyy-MM-ddTHH:mm:ss.SSSZ', // Ajustar el formato del parser
          unit: 'second',
          displayFormats: {
            second: 'HH:mm:ss',
          },
          tooltipFormat: 'yyyy-MM-dd HH:mm:ss',
        },
        ticks: {
          source: 'data', // Asegurar que las etiquetas provengan directamente de los datos
          maxTicksLimit: 7, // Limitar a 7 etiquetas en el eje x
          callback: function(value, index, values) {
            return new Date(value).toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
          },
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
          text: 'Temperatura (°C)',
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

export default TemperaturaChart;
