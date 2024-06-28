// ApagarMotor.js

import React, { useState } from 'react';
import { apagarMotor } from '../hooks/api';
import { handleChange } from './utils';

const ApagarMotor = () => {
    const [seconds, setSeconds] = useState(1);
    const [response, setResponse] = useState(null);
    const [error, setError] = useState(null);

    const handleApagar = async () => {
        try {
            const result = await apagarMotor(seconds);
            if (result.success) {
                setResponse({ message: 'Petición cerrar enviada al backend correctamente' });
                setError(null);
            } else {
                setResponse(null);
                setError({ message: 'Error en la petición al backend' });
            }
        } catch (error) {
            setResponse(null);
            setError({ message: 'Error de conexión con el backend' });
        }
    };

    return (
        <div>
            <h2>Cerrar</h2>
            <p>Temporizador en segundos</p>
            <input
                type="number"
                value={seconds}
                onChange={handleChange(setSeconds, 1, 120)}
                placeholder="Segundos"
                min="1"
                max="120"
            />
            <button onClick={handleApagar}>Cerrar</button>
            {response && <p style={{color: 'green'}}>{response.message}</p>}
            {error && <p style={{ color: 'red' }}>{error.message}</p>}
        </div>
    );
};

export default ApagarMotor;
