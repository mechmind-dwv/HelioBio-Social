import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ScatterChart, Scatter } from 'recharts';

interface SolarData {
  timestamp: string;
  kp_index: number;
  kp_status: string;
  sunspot_number: number;
  solar_wind_speed: number;
}

interface CorrelationData {
  correlation: number;
  p_value: number;
  p_value_corrected: number;
  confidence_interval: [number, number];
  effect_size: string;
  is_significant: boolean;
  n_observations: number;
}

const Dashboard: React.FC = () => {
  const [solarData, setSolarData] = useState<SolarData | null>(null);
  const [correlationData, setCorrelationData] = useState<CorrelationData | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'overview' | 'analysis' | 'about'>('overview');

  // Simulated data for demo
  useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      setSolarData({
        timestamp: new Date().toISOString(),
        kp_index: 3.7,
        kp_status: 'active',
        sunspot_number: 87,
        solar_wind_speed: 456.2
      });

      setCorrelationData({
        correlation: 0.43,
        p_value: 0.0008,
        p_value_corrected: 0.0024,
        confidence_interval: [0.28, 0.56],
        effect_size: 'medium',
        is_significant: true,
        n_observations: 156
      });

      setLoading(false);
    }, 500);
  }, []);

  // Simulated historical data
  const historicalData = Array.from({ length: 30 }, (_, i) => ({
    day: i + 1,
    kp: 2 + Math.random() * 4,
    anxiety: 50 + Math.random() * 30 + (2 + Math.random() * 4) * 3
  }));

  const getKpColor = (kp: number) => {
    if (kp < 3) return '#10b981'; // green
    if (kp < 5) return '#f59e0b'; // yellow
    if (kp < 7) return '#ef4444'; // red
    return '#991b1b'; // dark red
  };

  const getEffectSizeBadge = (size: string) => {
    const colors = {
      negligible: 'bg-gray-500',
      small: 'bg-blue-500',
      medium: 'bg-yellow-500',
      large: 'bg-red-500'
    };
    return colors[size as keyof typeof colors] || 'bg-gray-500';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading HelioBio-Social...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="text-3xl">🌞</div>
              <div>
                <h1 className="text-2xl font-bold">HelioBio-Social</h1>
                <p className="text-sm text-gray-400">Real-time Heliobiological Correlation Analysis</p>
              </div>
            </div>
            <div className="flex space-x-2">
              <button
                onClick={() => setActiveTab('overview')}
                className={`px-4 py-2 rounded ${activeTab === 'overview' ? 'bg-blue-600' : 'bg-gray-700'}`}
              >
                Overview
              </button>
              <button
                onClick={() => setActiveTab('analysis')}
                className={`px-4 py-2 rounded ${activeTab === 'analysis' ? 'bg-blue-600' : 'bg-gray-700'}`}
              >
                Analysis
              </button>
              <button
                onClick={() => setActiveTab('about')}
                className={`px-4 py-2 rounded ${activeTab === 'about' ? 'bg-blue-600' : 'bg-gray-700'}`}
              >
                About
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Scientific Disclaimer */}
      <div className="bg-yellow-900 border-l-4 border-yellow-500 p-4 max-w-7xl mx-auto mt-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-yellow-300" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <p className="text-sm text-yellow-200">
              <strong>Research Platform:</strong> This system analyzes correlations for scientific research. 
              Correlation ≠ Causation. All findings require peer review and independent replication.
            </p>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-6">
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Current Solar Activity */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                <h3 className="text-sm font-medium text-gray-400 mb-2">Kp Index</h3>
                <div className="flex items-end justify-between">
                  <div>
                    <div className="text-4xl font-bold" style={{ color: getKpColor(solarData?.kp_index || 0) }}>
                      {solarData?.kp_index.toFixed(1)}
                    </div>
                    <div className="text-sm text-gray-400 mt-1 capitalize">
                      {solarData?.kp_status}
                    </div>
                  </div>
                  <div className="text-2xl">⚡</div>
                </div>
              </div>

              <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                <h3 className="text-sm font-medium text-gray-400 mb-2">Sunspot Number</h3>
                <div className="flex items-end justify-between">
                  <div>
                    <div className="text-4xl font-bold text-blue-400">
                      {solarData?.sunspot_number}
                    </div>
                    <div className="text-sm text-gray-400 mt-1">
                      Active regions
                    </div>
                  </div>
                  <div className="text-2xl">☀️</div>
                </div>
              </div>

              <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                <h3 className="text-sm font-medium text-gray-400 mb-2">Solar Wind</h3>
                <div className="flex items-end justify-between">
                  <div>
                    <div className="text-4xl font-bold text-purple-400">
                      {solarData?.solar_wind_speed.toFixed(0)}
                    </div>
                    <div className="text-sm text-gray-400 mt-1">
                      km/s
                    </div>
                  </div>
                  <div className="text-2xl">🌊</div>
                </div>
              </div>

              <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                <h3 className="text-sm font-medium text-gray-400 mb-2">Data Quality</h3>
                <div className="flex items-end justify-between">
                  <div>
                    <div className="text-4xl font-bold text-green-400">
                      Good
                    </div>
                    <div className="text-sm text-gray-400 mt-1">
                      NOAA SWPC
                    </div>
                  </div>
                  <div className="text-2xl">✓</div>
                </div>
              </div>
            </div>

            {/* Time Series Chart */}
            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <h3 className="text-lg font-semibold mb-4">30-Day Trend: Kp Index vs Anxiety Searches</h3>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={historicalData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="day" stroke="#9ca3af" />
                  <YAxis yAxisId="left" stroke="#9ca3af" />
                  <YAxis yAxisId="right" orientation="right" stroke="#9ca3af" />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}
                    labelStyle={{ color: '#f3f4f6' }}
                  />
                  <Legend />
                  <Line 
                    yAxisId="left"
                    type="monotone" 
                    dataKey="kp" 
                    stroke="#ef4444" 
                    strokeWidth={2}
                    name="Kp Index"
                    dot={{ fill: '#ef4444' }}
                  />
                  <Line 
                    yAxisId="right"
                    type="monotone" 
                    dataKey="anxiety" 
                    stroke="#3b82f6" 
                    strokeWidth={2}
                    name="Anxiety Index"
                    dot={{ fill: '#3b82f6' }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* Correlation Results */}
            {correlationData && (
              <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                <h3 className="text-lg font-semibold mb-4">Correlation Analysis: Kp Index → Anxiety Searches</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-gray-700 rounded p-4">
                    <div className="text-sm text-gray-400 mb-1">Correlation Coefficient</div>
                    <div className="text-3xl font-bold text-blue-400">
                      {correlationData.correlation.toFixed(3)}
                    </div>
                    <div className="text-xs text-gray-500 mt-2">
                      95% CI: [{correlationData.confidence_interval[0].toFixed(2)}, {correlationData.confidence_interval[1].toFixed(2)}]
                    </div>
                  </div>

                  <div className="bg-gray-700 rounded p-4">
                    <div className="text-sm text-gray-400 mb-1">P-value (corrected)</div>
                    <div className="text-3xl font-bold text-green-400">
                      {correlationData.p_value_corrected.toFixed(4)}
                    </div>
                    <div className="text-xs text-gray-500 mt-2">
                      FDR-corrected (Benjamini-Hochberg)
                    </div>
                  </div>

                  <div className="bg-gray-700 rounded p-4">
                    <div className="text-sm text-gray-400 mb-1">Effect Size</div>
                    <div className="flex items-center space-x-2">
                      <span className={`px-3 py-1 rounded-full text-white font-semibold ${getEffectSizeBadge(correlationData.effect_size)}`}>
                        {correlationData.effect_size.toUpperCase()}
                      </span>
                    </div>
                    <div className="text-xs text-gray-500 mt-2">
                      n = {correlationData.n_observations} observations
                    </div>
                  </div>
                </div>

                {correlationData.is_significant && (
                  <div className="mt-4 p-4 bg-green-900 bg-opacity-30 border border-green-700 rounded">
                    <p className="text-sm text-green-200">
                      ✓ Statistically significant correlation detected (p &lt; 0.05 after FDR correction).
                      This suggests a moderate positive relationship worthy of further investigation.
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {activeTab === 'analysis' && (
          <div className="space-y-6">
            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <h3 className="text-lg font-semibold mb-4">Scientific Methodology</h3>
              <div className="space-y-4 text-gray-300">
                <div>
                  <h4 className="font-semibold text-white mb-2">Correlation Analysis</h4>
                  <ul className="list-disc list-inside space-y-1 text-sm">
                    <li>Pearson/Spearman correlation with bootstrap confidence intervals</li>
                    <li>FDR correction (Benjamini-Hochberg) for multiple comparisons</li>
                    <li>Effect size classification (Cohen's conventions)</li>
                    <li>Minimum 30 observations required</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-semibold text-white mb-2">Granger Causality</h4>
                  <ul className="list-disc list-inside space-y-1 text-sm">
                    <li>Tests if solar activity predicts mental health indicators</li>
                    <li>Stationarity checks (Augmented Dickey-Fuller test)</li>
                    <li>Optimal lag selection (1-30 days)</li>
                    <li>Bidirectional testing to rule out reverse causality</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-semibold text-white mb-2">Control Variables</h4>
                  <ul className="list-disc list-inside space-y-1 text-sm">
                    <li>Temperature and weather patterns</li>
                    <li>Day of week and seasonal effects</li>
                    <li>Economic indicators (unemployment, market volatility)</li>
                    <li>Major events (holidays, elections, disasters)</li>
                  </ul>
                </div>
              </div>
            </div>

            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <h3 className="text-lg font-semibold mb-4">Limitations & Considerations</h3>
              <div className="space-y-2 text-sm text-gray-300">
                <p>• <strong>Correlation ≠ Causation:</strong> Statistical associations do not prove causal mechanisms</p>
                <p>• <strong>Confounding Variables:</strong> Many factors influence mental health beyond solar activity</p>
                <p>• <strong>Ecological Fallacy:</strong> Population-level correlations don't apply to individuals</p>
                <p>• <strong>Data Quality:</strong> Proxy measures (e.g., Google Trends) have limitations</p>
                <p>• <strong>Publication Bias:</strong> Null results are important and should be reported</p>
                <p>• <strong>Replication:</strong> Findings require independent verification</p>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'about' && (
          <div className="space-y-6">
            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <h3 className="text-2xl font-semibold mb-4">About HelioBio-Social</h3>
              <div className="prose prose-invert max-w-none">
                <p className="text-gray-300 mb-4">
                  HelioBio-Social is an open-source research platform for investigating correlations 
                  between solar activity and terrestrial phenomena, particularly mental health indicators.
                </p>
                <p className="text-gray-300 mb-4">
                  Inspired by the pioneering work of Alexander Chizhevsky (1897-1964), who proposed 
                  connections between solar cycles and historical events, this project applies modern 
                  statistical methods to rigorously test heliobiological hypotheses.
                </p>
                <h4 className="text-xl font-semibold text-white mt-6 mb-3">Data Sources</h4>
                <ul className="list-disc list-inside space-y-1 text-gray-300">
                  <li>NOAA Space Weather Prediction Center (solar data)</li>
                  <li>NASA DONKI (space weather events)</li>
                  <li>WHO Global Health Observatory (mental health data)</li>
                  <li>Google Trends (population-level behavioral indicators)</li>
                </ul>
                <h4 className="text-xl font-semibold text-white mt-6 mb-3">Open Science</h4>
                <p className="text-gray-300">
                  All code, data, and analyses are publicly available on GitHub. We encourage:
                </p>
                <ul className="list-disc list-inside space-y-1 text-gray-300">
                  <li>Independent replication of our findings</li>
                  <li>Contributions to methodology and codebase</li>
                  <li>Peer review and constructive criticism</li>
                  <li>Collaborative research partnerships</li>
                </ul>
              </div>
            </div>

            <div className="bg-blue-900 bg-opacity-30 border border-blue-700 rounded-lg p-6">
              <h4 className="text-lg font-semibold mb-2">Get Involved</h4>
              <p className="text-gray-300 mb-4">
                This project thrives on community contributions. Whether you're a data scientist, 
                researcher, or curious citizen scientist, you can help advance heliobiological research.
              </p>
              <div className="flex space-x-4">
                <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded font-semibold">
                  View on GitHub
                </button>
                <button className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded font-semibold">
                  Read Documentation
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <footer className="bg-gray-800 border-t border-gray-700 mt-12">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex justify-between items-center text-sm text-gray-400">
            <div>
              HelioBio-Social v2.0.1 | MIT License | Open Source
            </div>
            <div>
              Data: NOAA SWPC | Updated: {new Date().toLocaleString()}
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Dashboard;
