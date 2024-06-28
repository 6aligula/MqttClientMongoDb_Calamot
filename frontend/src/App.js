import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import './css/Style.css';
import Home from './screens/Home';
import HumedadTierra from './components/HumedadTierraChart';
import MotorScreen from './screens/MotorScreen';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/humedadtierra" element={<HumedadTierra />} />
        <Route path="/humedadtierra" element={<HumedadTierra />} />
        <Route path="/motorScreen" element={<MotorScreen />} />
      </Routes>
    </Router>
  );
}

export default App;
