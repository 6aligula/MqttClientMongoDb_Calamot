import { useEffect, useState } from 'react';
import fetchDataFromApi from './fetchDataFromApi';

const useFetchData = () => {
  const [data, setData] = useState({ mediana: [], timestamp: [], ultimas_temperaturas: [], humedad: [] });
  const [error, setError] = useState(null);

  const fetchData = async () => {
    //console.log('Fetching data...');
    try {
      const [newDataTemp, newDataHumedad] = await Promise.all([
        fetchDataFromApi('temperatura'),
        fetchDataFromApi('humedad')
      ]);

      //console.log('New temperature data from API:', newDataTemp);
      //console.log('New humidity data from API:', newDataHumedad);

      const updatedData = {
        mediana: newDataTemp.mediana,
        timestamp: newDataTemp.timestamp,
        ultimas_temperaturas: newDataTemp.ultimas_temperaturas,
        humedad: newDataHumedad.map(item => ({ y: item.humedad, x: new Date(item.timestamp) })),
      };

      //console.log('Updated data before setting state:', updatedData);
      setData(updatedData);
      //console.log('Updated data:', updatedData);
    } catch (error) {
      setError(error.message);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(() => {
      fetchData();
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  return { data, error };
};

export default useFetchData;
