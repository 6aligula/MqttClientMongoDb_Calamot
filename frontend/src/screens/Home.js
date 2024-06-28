import React from 'react';
import { useNavigate } from 'react-router-dom';
import useFetchData from '../hooks/useFetchData';
import HumedadChart from '../components/HumedadChart';
import TemperaturaChart from '../components/TemperaturaChart';

const Home = () => {
  const { data } = useFetchData();
  const navigate = useNavigate();
  //console.log('Data in Home component:', data);

  return (
    <div className="App">
      <header className="App-header">
        <h1>Jardinería</h1>
        <div className="button-container">
          <button onClick={() => navigate('/humedadtierra')}>Humedad Tierra</button>
          <button onClick={() => navigate('/motorScreen')}>Motor Control</button>
        </div>
        <div className="data-container">
          <div className="data-block">
            <h1>Humedad</h1>
            {data.humedad.length > 0 ? <HumedadChart data={data} /> : <p>Cargando...</p>}
          </div>
          <div className="data-block">
            <h1>Temperatura</h1>
            {data.ultimas_temperaturas && data.ultimas_temperaturas.length > 0 ? (
              <div>
                <p>Mediana: {data.mediana}°C</p>
                <TemperaturaChart data={data} />
              </div>
            ) : (
              <p>Cargando...</p>
            )}
          </div>
        </div>
      </header>
    </div>
  );
};

export default Home;
