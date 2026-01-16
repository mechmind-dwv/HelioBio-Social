import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

interface CorrelationResult {
  date: string;
  kp_index: number;
  mental_health_index: number;
  correlation: number;
  p_value: number;
}

const DashboardMVP: React.FC = () => {
  const [data, setData] = useState<CorrelationResult[]>([]);
  const [summary, setSummary] = useState<any>(null);
  
  useEffect(() => {
    fetchData();
  }, []);
  
  const fetchData = async () => {
    try {
      const response = await fetch('/api/v1/correlation/latest');
      const result = await response.json();
      setData(result.data);
      setSummary(result.summary);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };
  
  return (
    <div className="dashboard-mvp">
      <h1>🌞 HelioBio-Scientific MVP</h1>
      
      {summary && (
        <div className="summary-card">
          <h2>Resumen Estadístico</h2>
          <p><strong>Correlación:</strong> {summary.correlation.toFixed(3)}</p>
          <p><strong>Valor p:</strong> {summary.p_value.toFixed(4)}</p>
          <p><strong>Significativo:</strong> 
            <span className={summary.is_significant ? 'significant' : 'not-significant'}>
              {summary.is_significant ? ' ✅ Sí' : ' ❌ No'}
            </span>
          </p>
        </div>
      )}
      
      <div className="chart-container">
        <h2>Correlación Temporal</h2>
        <LineChart width={800} height={400} data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis yAxisId="left" />
          <YAxis yAxisId="right" orientation="right" />
          <Tooltip />
          <Legend />
          <Line 
            yAxisId="left"
            type="monotone" 
            dataKey="kp_index" 
            stroke="#8884d8" 
            name="Índice Kp" 
          />
          <Line 
            yAxisId="right"
            type="monotone" 
            dataKey="mental_health_index" 
            stroke="#82ca9d" 
            name="Salud Mental" 
          />
        </LineChart>
      </div>
      
      <div className="scientific-context">
        <h3>🧪 Contexto Científico</h3>
        <p>
          Esta visualización muestra la correlación entre el índice Kp 
          (actividad geomagnética, datos de NOAA) y un índice de salud mental 
          (datos de OMS/CDC). Una correlación positiva sugiere que la 
          actividad solar podría estar relacionada con variaciones en 
          indicadores de salud mental.
        </p>
      </div>
    </div>
  );
};

export default DashboardMVP;
