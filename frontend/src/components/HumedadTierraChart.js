// HumedadTierraChart.js
import React from 'react';
import { Line } from 'react-chartjs-2';
import { Link } from 'react-router-dom';
import useFetchHumedadData from '../hooks/useFetchHumedadData';
import {
  Chart as ChartJS,
  TimeScale,
  LinearScale,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import 'chartjs-adapter-date-fns';
import './css/HumedadTierraChart.css';

ChartJS.register(TimeScale, LinearScale, LineElement, PointElement, Title, Tooltip, Legend);

const HumedadTierraChart = () => {
  const data = useFetchHumedadData('/humedad/tierra');

  const chartData = {
    labels: data.timestamp,
    datasets: [
      {
        label: 'Humedad Tierra',
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
          callback: function (value) {
            const date = new Date(value);
            return date.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
          },
          maxRotation: 0,
          minRotation: 0,
          sampleSize: 7,
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

  return (
    <div className="container">
      <div className="inner-container">
        <div className="flex-1"></div>
        <Link to="/" style={{ textDecoration: 'none' }}>
          <button className="home-button">Home</button>
        </Link>
        <h2 className="title">Humedad Tierra</h2>
        <div className="chart-container">
          <Line data={chartData} options={options} />
        </div>
      </div>
    </div>
  );
};

export default HumedadTierraChart;
