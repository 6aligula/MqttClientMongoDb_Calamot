// MotorScreen.js

import React from 'react';
import EncenderMotor from '../components/EncenderMotor';
import ApagarMotor from '../components/ApagarMotor';
import EstadoMotor from '../components/EstadoMotor';
import ControlMotor from '../components/ControlMotor';
import styles from '../css/MotorScreen.module.css'

const MotorScreen = () => {
    return (
        <div className={styles.container}>
            <h1 className={styles.title}>Programación del Motor</h1>
            <ControlMotor />
            <EstadoMotor />
            <h1 className={`${styles.title} ${styles.spacingTop}`}>Control manual de Motor</h1>
            <EncenderMotor />
            <ApagarMotor />
        </div>
    );
};

export default MotorScreen;
