// useFetchHumedadData.js
import { useState, useEffect, useCallback } from 'react';

const useFetchHumedadData = (url, interval = 5000) => {
  const [data, setData] = useState({ timestamp: [], humedad: [] });

  const fetchData = useCallback(() => {
    fetch(`${process.env.REACT_APP_API_URL}/${url}`)
      .then(response => {
        if (!response.ok) {
          throw new Error('Error en la respuesta de la red');
        }
        return response.json();
      })
      .then(newData => {
        setData({
          timestamp: newData.map(entry => new Date(entry.timestamp)),
          humedad: newData.map(entry => entry.humedad_tierra),
        });
      })
      .catch(error => {
        console.error('Error al obtener datos:', error);
      });
  }, [url]);

  useEffect(() => {
    fetchData();
    const intervalId = setInterval(fetchData, interval);
    return () => clearInterval(intervalId);
  }, [fetchData, interval]);

  return data;
};

export default useFetchHumedadData;
