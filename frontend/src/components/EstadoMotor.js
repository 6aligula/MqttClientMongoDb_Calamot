import React, { useState, useEffect } from 'react';
import MotorAnimation from './MotorAnimation';
import socketIOClient from 'socket.io-client';
import { getMotorEvents } from '../hooks/api';

const EstadoMotor = () => {
    const [estado, setEstado] = useState(null);
    const [error, setError] = useState(null);
    const [isConnected, setIsConnected] = useState(false);

    useEffect(() => {
        // Obtener el estado inicial del motor al cargar la página
        getMotorEvents()
            .then(data => {
                setEstado(data);
            })
            .catch(err => {
                console.error('Error al obtener el estado del motor:', err);
                setError('Error al obtener el estado del motor');
            });

        const socket = socketIOClient(process.env.REACT_APP_API_URL);

        socket.on('connect', () => {
            console.log('Connected to socket');
            setIsConnected(true);
        });

        socket.on('disconnect', () => {
            console.log('Disconected to socket');
            setIsConnected(false);
        });

        // socket.on('motor_state', (data) => {
        //     console.log(data);
        //     setEstado(data);
        // });
        socket.on('motor_state', (data) => {
            console.log(data);
            setEstado(data);
            if (data.state === 'error') {
                setError('Error en el estado del motor');
            } else {
                setError(null);
            }
        });

        socket.on('connect_error', (err) => {
            console.log(err);
            setError(err.message);
        });

        // Cleanup function to disconnect the socket when the component unmounts
        return () => {
            socket.disconnect();
        };
    }, []);

    return (
        <div>
            <h2>Estado del Motor</h2>
            {estado && (
                <div>
                    <p>Estado actual: {`Estado: ${estado.state} tu corazón, Duración: ${estado.duration} segundos de felicidad`}</p>
                    <MotorAnimation state={estado.state} duration={estado.duration} />
                </div>
            )}
            {error && <p style={{ color: 'red' }}>{error}</p>}
            {!isConnected && !error && <p style={{ color: 'orange' }}>Conectando...</p>}
        </div>
    );
};

export default EstadoMotor;
