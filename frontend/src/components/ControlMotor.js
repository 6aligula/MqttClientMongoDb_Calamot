import React from 'react';
import { useMotorConfig } from '../hooks/useMotorConfig';
import './css/ControlMotor.css';

const ControlMotor = () => {
    const { config, response, error, sendConfig, setConfig } = useMotorConfig();

    const handleSendConfigMotor = () => {
        const { umbral_alto, umbral_bajo, segundos } = config;
        sendConfig(umbral_alto, umbral_bajo, segundos);
    };

    const handleChangeUmbralAlto = (e) => {
        setConfig((prevConfig) => ({ ...prevConfig, umbral_alto: parseFloat(e.target.value) }));
    };

    const handleChangeUmbralBajo = (e) => {
        setConfig((prevConfig) => ({ ...prevConfig, umbral_bajo: parseFloat(e.target.value) }));
    };

    const handleChangeSegundos = (e) => {
        setConfig((prevConfig) => ({ ...prevConfig, segundos: parseInt(e.target.value, 10) }));
    };

    return (
        <div>
            <h2>Configurar control del motor</h2>
            <div>
                <label>Umbral Alto:</label>
                <input
                    type="number"
                    value={config.umbral_alto}
                    onChange={handleChangeUmbralAlto}
                />
            </div>
            <div>
                <label>Umbral Bajo:</label>
                <input
                    type="number"
                    value={config.umbral_bajo}
                    onChange={handleChangeUmbralBajo}
                />
            </div>
            <div>
                <label>Duración (seg):</label>
                <input
                    type="number"
                    value={config.segundos}
                    onChange={handleChangeSegundos}
                />
            </div>
            <button onClick={handleSendConfigMotor}>Enviar Configuración</button>
            {response && <p style={{color: 'green'}}>{response}</p>}
            {error && <p style={{ color: 'red' }}>{error}</p>}
        </div>
    );
};

export default ControlMotor;
