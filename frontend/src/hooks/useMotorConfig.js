import { useState, useEffect } from 'react';
import { getConfigGarden, sendConfigGarden } from './api';

export const useMotorConfig = () => {
    const [config, setConfig] = useState({ umbral_alto: 30, umbral_bajo: 10, segundos: 10 });
    const [response, setResponse] = useState(null);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchConfig = async () => {
            try {
                const data = await getConfigGarden();
                setConfig(data);
            } catch (err) {
                setError('Error obteniendo configuración');
                console.error(err);
            }
        };

        fetchConfig();
    }, []);

    const sendConfig = async (umbralAlto, umbralBajo, segundos) => {
        try {
            const data = await sendConfigGarden(umbralAlto, umbralBajo, segundos);
            setResponse(data.message);
            setError(null);
        } catch (err) {
            setError('Error enviando configuración');
            setResponse(null);
            console.error(err);
        }
    };

    return { config, response, error, sendConfig, setConfig };
};
