import React, { useEffect } from 'react';
import { useSpring, animated } from '@react-spring/web';
import './css/MotorAnimation.css';

const MotorAnimation = ({ state, duration }) => {
    console.log('MotorAnimation props:', { state, duration });

    const [styles, api] = useSpring(() => ({
        from: { width: '0%' },
        width: '0%',
        config: { duration: duration * 1000 },
        reset: true
    }));

    useEffect(() => {
        // api.start({ width: '100%', reset: true });
        api.start({ width: '100%', config: { duration: duration * 1000 }, reset: true });
    }, [state, api]);

    return (
        <div className="motor-animation-container">
            <animated.div className={`motor-animation ${state}`} style={styles}></animated.div>
            <p>{state === 'abrir' ? 'Abriendo...' : 'Cerrando...'}</p>
        </div>
    );
};

export default MotorAnimation;
