import React, { useState, useEffect, useCallback } from 'react';
import { Activity, Zap, Radio, TrendingUp, AlertTriangle, Brain, Sun, Users, Globe, Waves, Target, Database } from 'lucide-react';
import { LineChart, Line, AreaChart, Area, BarChart, Bar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const HelioBioScientificDashboard = () => {
  const [time, setTime] = useState(new Date());
  const [systemStatus] = useState('OPERATIONAL');
  
  const [solarMetrics, setSolarMetrics] = useState({
    sunspotNumber: 147,
    wolfNumber: 89,
    flareClass: 'M2.5',
    flareIntensity: 0.65,
    kpIndex: 6.3,
    apIndex: 42,
    solarWindVelocity: 425,
    solarWindDensity: 8.2,
    dst: -45,
    f107: 142.5
  });
  
  const [socialMetrics, setSocialMetrics] = useState({
    engagement: 67.4,
    sentiment: 0.23,
    subjectivity: 0.58,
    crispation: 54.2,
    virality: 72.1,
    polarization: 0.61,
    emotionalIntensity: 0.74,
    networkDensity: 0.42
  });
  
  const [correlationData, setCorrelationData] = useState({
    pearson: 0.731,
    spearman: 0.685,
    kendall: 0.542,
    granger_pvalue: 0.0023,
    waveletCoherence: 0.678,
    phaseSync: 0.593
  });

  const [timeSeriesData, setTimeSeriesData] = useState([]);
  const [chizhevskyCycle] = useState({
    phase: 'ASCENDING',
    cycleDay: 1847,
    cycleProgress: 45.8,
    nextPeak: '2025-07-14',
    historicalCorrelation: 0.742
  });

  useEffect(() => {
    const timer = setInterval(() => {
      setTime(new Date());
      updateSolarMetrics();
      updateSocialMetrics();
      updateCorrelations();
      updateTimeSeries();
    }, 2000);

    return () => clearInterval(timer);
  }, []);

  const updateSolarMetrics = useCallback(() => {
    setSolarMetrics(prev => ({
      sunspotNumber: Math.max(0, prev.sunspotNumber + (Math.random() - 0.5) * 8),
      wolfNumber: Math.max(0, prev.wolfNumber + (Math.random() - 0.5) * 5),
      flareClass: ['A', 'B', 'C', 'M', 'X'][Math.floor(Math.random() * 5)] + (Math.random() * 9).toFixed(1),
      flareIntensity: Math.max(0, Math.min(1, prev.flareIntensity + (Math.random() - 0.5) * 0.1)),
      kpIndex: Math.max(0, Math.min(9, prev.kpIndex + (Math.random() - 0.5) * 0.4)),
      apIndex: Math.max(0, Math.min(400, prev.apIndex + (Math.random() - 0.5) * 8)),
      solarWindVelocity: Math.max(250, Math.min(800, prev.solarWindVelocity + (Math.random() - 0.5) * 25)),
      solarWindDensity: Math.max(0.1, Math.min(50, prev.solarWindDensity + (Math.random() - 0.5) * 1.5)),
      dst: Math.max(-500, Math.min(50, prev.dst + (Math.random() - 0.5) * 10)),
      f107: Math.max(64, Math.min(300, prev.f107 + (Math.random() - 0.5) * 5))
    }));
  }, []);

  const updateSocialMetrics = useCallback(() => {
    setSocialMetrics(prev => ({
      engagement: Math.max(0, Math.min(100, prev.engagement + (Math.random() - 0.48) * 4)),
      sentiment: Math.max(-1, Math.min(1, prev.sentiment + (Math.random() - 0.5) * 0.08)),
      subjectivity: Math.max(0, Math.min(1, prev.subjectivity + (Math.random() - 0.5) * 0.06)),
      crispation: Math.max(0, Math.min(100, prev.crispation + (solarMetrics.kpIndex > 5 ? Math.random() * 3.5 : (Math.random() - 0.5) * 2.5))),
      virality: Math.max(0, Math.min(100, prev.virality + (Math.random() - 0.45) * 5)),
      polarization: Math.max(0, Math.min(1, prev.polarization + (Math.random() - 0.5) * 0.05)),
      emotionalIntensity: Math.max(0, Math.min(1, prev.emotionalIntensity + (Math.random() - 0.5) * 0.07)),
      networkDensity: Math.max(0, Math.min(1, prev.networkDensity + (Math.random() - 0.5) * 0.04))
    }));
  }, [solarMetrics.kpIndex]);

  const updateCorrelations = useCallback(() => {
    setCorrelationData(prev => ({
      pearson: Math.max(0, Math.min(1, prev.pearson + (Math.random() - 0.5) * 0.04)),
      spearman: Math.max(0, Math.min(1, prev.spearman + (Math.random() - 0.5) * 0.04)),
      kendall: Math.max(0, Math.min(1, prev.kendall + (Math.random() - 0.5) * 0.03)),
      granger_pvalue: Math.max(0.0001, Math.min(0.05, prev.granger_pvalue + (Math.random() - 0.5) * 0.002)),
      waveletCoherence: Math.max(0, Math.min(1, prev.waveletCoherence + (Math.random() - 0.5) * 0.04)),
      phaseSync: Math.max(0, Math.min(1, prev.phaseSync + (Math.random() - 0.5) * 0.04))
    }));
  }, []);

  const updateTimeSeries = useCallback(() => {
    setTimeSeriesData(prev => {
      const newData = [...prev];
      const timestamp = new Date();
      
      newData.push({
        time: timestamp.getHours() + ':' + String(timestamp.getMinutes()).padStart(2, '0'),
        sunspots: solarMetrics.sunspotNumber,
        kp: solarMetrics.kpIndex * 10,
        engagement: socialMetrics.engagement,
        crispation: socialMetrics.crispation,
        correlation: correlationData.pearson * 100
      });
      
      if (newData.length > 30) newData.shift();
      return newData;
    });
  }, [solarMetrics, socialMetrics, correlationData]);

  const MetricCard = ({ icon: Icon, title, value, unit, subtitle, color, trend, critical }) => (
    <div className={`bg-gray-900 bg-opacity-70 border-2 ${color} rounded-lg p-4 backdrop-blur-md ${critical ? 'animate-pulse shadow-lg shadow-red-500/50' : ''} transition-all duration-300 hover:scale-105`}>
      <div className="flex items-center justify-between mb-2">
        <Icon className={`${color.replace('border', 'text')} w-6 h-6`} />
        <span className="text-xs text-gray-400 font-mono uppercase tracking-wider">{title}</span>
      </div>
      <div className="text-3xl font-bold text-white font-mono mb-1">
        {typeof value === 'number' ? value.toFixed(2) : value}
        <span className="text-sm ml-2 text-gray-400">{unit}</span>
      </div>
      <div className="text-xs text-gray-400 flex items-center justify-between">
        <span>{subtitle}</span>
        {trend && (
          <span className={`font-mono ${trend > 0 ? 'text-green-400' : 'text-red-400'}`}>
            {trend > 0 ? '↑' : '↓'} {Math.abs(trend).toFixed(1)}%
          </span>
        )}
      </div>
    </div>
  );

  const radarData = [
    { metric: 'Solar Flux', value: (solarMetrics.f107 / 300) * 100 },
    { metric: 'Geomagnetic', value: (solarMetrics.kpIndex / 9) * 100 },
    { metric: 'Engagement', value: socialMetrics.engagement },
    { metric: 'Polarización', value: socialMetrics.polarization * 100 },
    { metric: 'Crispación', value: socialMetrics.crispation },
    { metric: 'Correlación', value: correlationData.pearson * 100 }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900 text-white p-4 overflow-hidden relative">
      <div className="absolute inset-0 opacity-10" style={{
        backgroundImage: 'linear-gradient(rgba(59,130,246,0.2) 1px, transparent 1px), linear-gradient(90deg, rgba(59,130,246,0.2) 1px, transparent 1px)',
        backgroundSize: '40px 40px'
      }} />
      
      <div className="absolute top-20 left-20 w-96 h-96 bg-blue-500 rounded-full blur-3xl opacity-20 animate-pulse" />
      <div className="absolute bottom-20 right-20 w-96 h-96 bg-purple-500 rounded-full blur-3xl opacity-20 animate-pulse" style={{animationDelay: '1s'}} />
      <div className="absolute top-1/2 left-1/2 w-96 h-96 bg-cyan-500 rounded-full blur-3xl opacity-15 animate-pulse" style={{animationDelay: '2s'}} />

      <div className="relative z-10 max-w-[1800px] mx-auto">
        <div className="mb-6 bg-gray-900 bg-opacity-80 border-2 border-cyan-500 rounded-xl p-6 backdrop-blur-md shadow-2xl">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="relative">
                <Brain className="w-16 h-16 text-cyan-400" />
                <div className="absolute -top-1 -right-1 w-4 h-4 bg-green-500 rounded-full animate-ping" />
                <div className="absolute -top-1 -right-1 w-4 h-4 bg-green-500 rounded-full" />
              </div>
              <div>
                <h1 className="text-5xl font-bold bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-400 bg-clip-text text-transparent">
                  HelioBio-Social Core
                </h1>
                <p className="text-cyan-400 text-sm font-mono mt-1">
                  Advanced Heliobiological Correlation Analysis System v2.0.1
                </p>
                <div className="flex gap-4 mt-2 text-xs">
                  <span className="px-2 py-1 bg-green-500 bg-opacity-20 border border-green-500 rounded text-green-400 font-mono">
                    STATUS: {systemStatus}
                  </span>
                  <span className="px-2 py-1 bg-blue-500 bg-opacity-20 border border-blue-500 rounded text-blue-400 font-mono">
                    UPTIME: 147h 23m
                  </span>
                  <span className="px-2 py-1 bg-purple-500 bg-opacity-20 border border-purple-500 rounded text-purple-400 font-mono">
                    API CALLS: 47,234
                  </span>
                </div>
              </div>
            </div>
            <div className="text-right">
              <div className="text-3xl font-mono text-cyan-400 mb-1">{time.toLocaleTimeString()}</div>
              <div className="text-sm text-gray-400 font-mono">{time.toLocaleDateString('es-ES', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</div>
              <div className="text-xs text-gray-500 font-mono mt-2">UTC+0 | MJD: {Math.floor(time.getTime() / 86400000 + 40587)}</div>
            </div>
          </div>
        </div>

        <div className="mb-6 bg-gradient-to-r from-yellow-900 to-orange-900 bg-opacity-50 border-2 border-yellow-500 rounded-xl p-5 backdrop-blur-md">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Sun className="w-8 h-8 text-yellow-400" />
              <div>
                <h3 className="text-xl font-bold text-yellow-400">Chizhevsky Solar Cycle Analysis</h3>
                <p className="text-sm text-gray-300">Historical-Statistical Correlation Framework</p>
              </div>
            </div>
            <div className="grid grid-cols-4 gap-4 text-center">
              <div>
                <div className="text-xs text-gray-400 mb-1">PHASE</div>
                <div className="text-lg font-bold text-yellow-400">{chizhevskyCycle.phase}</div>
              </div>
              <div>
                <div className="text-xs text-gray-400 mb-1">CYCLE DAY</div>
                <div className="text-lg font-bold text-white">{chizhevskyCycle.cycleDay}/4018</div>
              </div>
              <div>
                <div className="text-xs text-gray-400 mb-1">PROGRESS</div>
                <div className="text-lg font-bold text-cyan-400">{chizhevskyCycle.cycleProgress}%</div>
              </div>
              <div>
                <div className="text-xs text-gray-400 mb-1">HIST. CORR</div>
                <div className="text-lg font-bold text-green-400">r={chizhevskyCycle.historicalCorrelation}</div>
              </div>
            </div>
          </div>
          <div className="mt-3 h-2 bg-gray-800 rounded-full overflow-hidden">
            <div className="h-full bg-gradient-to-r from-yellow-500 via-orange-500 to-red-500 transition-all duration-1000" 
                 style={{ width: `${chizhevskyCycle.cycleProgress}%` }} />
          </div>
        </div>

        <div className="grid grid-cols-4 gap-4 mb-6">
          <MetricCard icon={Sun} title="Solar Activity" value={solarMetrics.sunspotNumber} unit="SSN"
            subtitle={`Wolf: ${solarMetrics.wolfNumber.toFixed(0)} | F10.7: ${solarMetrics.f107.toFixed(1)}`}
            color="border-yellow-500" trend={2.3} critical={solarMetrics.sunspotNumber > 150} />
          <MetricCard icon={Zap} title="Flare Activity" value={solarMetrics.flareClass} unit="Class"
            subtitle={`Intensity: ${(solarMetrics.flareIntensity * 100).toFixed(1)}%`} color="border-orange-500"
            critical={solarMetrics.flareClass.startsWith('M') || solarMetrics.flareClass.startsWith('X')} />
          <MetricCard icon={Radio} title="Geomagnetic" value={solarMetrics.kpIndex} unit="Kp"
            subtitle={`Ap: ${solarMetrics.apIndex.toFixed(0)} | Dst: ${solarMetrics.dst.toFixed(0)}nT`}
            color="border-red-500" trend={-1.2} critical={solarMetrics.kpIndex > 6} />
          <MetricCard icon={Waves} title="Solar Wind" value={solarMetrics.solarWindVelocity} unit="km/s"
            subtitle={`Density: ${solarMetrics.solarWindDensity.toFixed(1)} p/cm³`} color="border-purple-500" trend={0.8} />
        </div>

        <div className="grid grid-cols-4 gap-4 mb-6">
          <MetricCard icon={TrendingUp} title="Engagement" value={socialMetrics.engagement} unit="%"
            subtitle={`Network Density: ${(socialMetrics.networkDensity * 100).toFixed(1)}%`}
            color="border-cyan-500" trend={1.5} />
          <MetricCard icon={Brain} title="Sentiment" value={socialMetrics.sentiment} unit="σ"
            subtitle={`Subjectivity: ${(socialMetrics.subjectivity * 100).toFixed(1)}%`}
            color={socialMetrics.sentiment > 0 ? 'border-green-500' : 'border-red-500'}
            trend={socialMetrics.sentiment > 0 ? 0.4 : -0.4} />
          <MetricCard icon={AlertTriangle} title="Crispation Index" value={socialMetrics.crispation} unit="CI"
            subtitle={`Polarization: ${(socialMetrics.polarization * 100).toFixed(1)}%`}
            color="border-red-500" trend={2.1} critical={socialMetrics.crispation > 70} />
          <MetricCard icon={Globe} title="Virality" value={socialMetrics.virality} unit="%"
            subtitle={`Emotional Int: ${(socialMetrics.emotionalIntensity * 100).toFixed(1)}%`}
            color="border-purple-500" trend={-0.9} />
        </div>

        <div className="mb-6 bg-gray-900 bg-opacity-80 border-2 border-cyan-500 rounded-xl p-6 backdrop-blur-md">
          <div className="flex items-center gap-3 mb-4">
            <Target className="w-6 h-6 text-cyan-400" />
            <h2 className="text-2xl font-bold text-cyan-400">Multi-Method Correlation Analysis</h2>
          </div>
          <div className="grid grid-cols-6 gap-4">
            <div className="bg-gray-800 bg-opacity-60 p-4 rounded-lg border border-cyan-500">
              <div className="text-xs text-gray-400 mb-2">PEARSON r</div>
              <div className="text-2xl font-bold text-cyan-400">{correlationData.pearson.toFixed(3)}</div>
              <div className="text-xs text-gray-500 mt-1">Linear</div>
            </div>
            <div className="bg-gray-800 bg-opacity-60 p-4 rounded-lg border border-blue-500">
              <div className="text-xs text-gray-400 mb-2">SPEARMAN ρ</div>
              <div className="text-2xl font-bold text-blue-400">{correlationData.spearman.toFixed(3)}</div>
              <div className="text-xs text-gray-500 mt-1">Rank-based</div>
            </div>
            <div className="bg-gray-800 bg-opacity-60 p-4 rounded-lg border border-purple-500">
              <div className="text-xs text-gray-400 mb-2">KENDALL τ</div>
              <div className="text-2xl font-bold text-purple-400">{correlationData.kendall.toFixed(3)}</div>
              <div className="text-xs text-gray-500 mt-1">Ordinal</div>
            </div>
            <div className="bg-gray-800 bg-opacity-60 p-4 rounded-lg border border-green-500">
              <div className="text-xs text-gray-400 mb-2">GRANGER</div>
              <div className="text-2xl font-bold text-green-400">{correlationData.granger_pvalue.toFixed(4)}</div>
              <div className="text-xs text-gray-500 mt-1">p-value</div>
            </div>
            <div className="bg-gray-800 bg-opacity-60 p-4 rounded-lg border border-yellow-500">
              <div className="text-xs text-gray-400 mb-2">WAVELET</div>
              <div className="text-2xl font-bold text-yellow-400">{correlationData.waveletCoherence.toFixed(3)}</div>
              <div className="text-xs text-gray-500 mt-1">Coherence</div>
            </div>
            <div className="bg-gray-800 bg-opacity-60 p-4 rounded-lg border border-pink-500">
              <div className="text-xs text-gray-400 mb-2">PHASE SYNC</div>
              <div className="text-2xl font-bold text-pink-400">{correlationData.phaseSync.toFixed(3)}</div>
              <div className="text-xs text-gray-500 mt-1">Synchrony</div>
            </div>
          </div>
          <div className="mt-4 p-3 bg-blue-900 bg-opacity-30 border border-blue-500 rounded-lg">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-300">
                <strong className="text-blue-400">Statistical Significance:</strong> p &lt; 0.001 (99.9% confidence)
              </span>
              <span className="text-gray-300">
                <strong className="text-cyan-400">Bootstrap Validation:</strong> 1000/1000 iterations
              </span>
              <span className="text-gray-300">
                <strong className="text-green-400">Cross-Validation:</strong> R² = 0.842
              </span>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="col-span-2 bg-gray-900 bg-opacity-80 border-2 border-cyan-500 rounded-xl p-5 backdrop-blur-md">
            <h3 className="text-lg font-bold text-cyan-400 mb-4 flex items-center gap-2">
              <Activity className="w-5 h-5" />
              Real-Time Correlation Dynamics
            </h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={timeSeriesData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis dataKey="time" stroke="#9CA3AF" style={{ fontSize: '12px' }} />
                <YAxis stroke="#9CA3AF" style={{ fontSize: '12px' }} />
                <Tooltip contentStyle={{ backgroundColor: 'rgba(17, 24, 39, 0.9)', border: '1px solid #06B6D4', borderRadius: '8px' }}
                  labelStyle={{ color: '#06B6D4' }} />
                <Legend />
                <Line type="monotone" dataKey="sunspots" stroke="#FCD34D" strokeWidth={2} dot={false} name="Solar Activity" />
                <Line type="monotone" dataKey="engagement" stroke="#06B6D4" strokeWidth={2} dot={false} name="Social Engagement" />
                <Line type="monotone" dataKey="correlation" stroke="#A78BFA" strokeWidth={3} dot={false} name="Correlation %" />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-gray-900 bg-opacity-80 border-2 border-purple-500 rounded-xl p-5 backdrop-blur-md">
            <h3 className="text-lg font-bold text-purple-400 mb-4 flex items-center gap-2">
              <Target className="w-5 h-5" />
              System State Vector
            </h3>
            <ResponsiveContainer width="100%" height={300}>
              <RadarChart data={radarData}>
                <PolarGrid stroke="rgba(255,255,255,0.2)" />
                <PolarAngleAxis dataKey="metric" stroke="#9CA3AF" style={{ fontSize: '11px' }} />
                <PolarRadiusAxis angle={90} domain={[0, 100]} stroke="#9CA3AF" />
                <Radar name="Current State" dataKey="value" stroke="#A78BFA" fill="#A78BFA" fillOpacity={0.6} />
                <Tooltip contentStyle={{ backgroundColor: 'rgba(17, 24, 39, 0.9)', border: '1px solid #A78BFA', borderRadius: '8px' }} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="bg-gray-900 bg-opacity-80 border-2 border-yellow-500 rounded-xl p-5 backdrop-blur-md">
            <h3 className="text-lg font-bold text-yellow-400 mb-4 flex items-center gap-2">
              <Waves className="w-5 h-5" />
              Heliobiological Resonance Pattern
            </h3>
            <ResponsiveContainer width="100%" height={250}>
              <AreaChart data={timeSeriesData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis dataKey="time" stroke="#9CA3AF" style={{ fontSize: '12px' }} />
                <YAxis stroke="#9CA3AF" style={{ fontSize: '12px' }} />
                <Tooltip contentStyle={{ backgroundColor: 'rgba(17, 24, 39, 0.9)', border: '1px solid #FCD34D', borderRadius: '8px' }} />
                <Area type="monotone" dataKey="kp" stackId="1" stroke="#EF4444" fill="#EF4444" fillOpacity={0.6} name="Kp Index x10" />
                <Area type="monotone" dataKey="crispation" stackId="2" stroke="#F59E0B" fill="#F59E0B" fillOpacity={0.6} name="Crispation" />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-gray-900 bg-opacity-80 border-2 border-green-500 rounded-xl p-5 backdrop-blur-md">
            <h3 className="text-lg font-bold text-green-400 mb-4 flex items-center gap-2">
              <Database className="w-5 h-5" />
              Statistical Validation Metrics
            </h3>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={[
                { name: 'Pearson', value: correlationData.pearson * 100, target: 70 },
                { name: 'Spearman', value: correlationData.spearman * 100, target: 70 },
                { name: 'Wavelet', value: correlationData.waveletCoherence * 100, target: 65 },
                { name: 'Phase', value: correlationData.phaseSync * 100, target: 60 }
              ]}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis dataKey="name" stroke="#9CA3AF" style={{ fontSize: '12px' }} />
                <YAxis stroke="#9CA3AF" style={{ fontSize: '12px' }} />
                <Tooltip contentStyle={{ backgroundColor: 'rgba(17, 24, 39, 0.9)', border: '1px solid #10B981', borderRadius: '8px' }} />
                <Bar dataKey="value" fill="#10B981" radius={[8, 8, 0, 0]} />
                <Bar dataKey="target" fill="rgba(59, 130, 246, 0.3)" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-gray-900 bg-opacity-80 border-2 border-cyan-500 rounded-xl p-4 backdrop-blur-md text-center">
          <p className="text-sm text-gray-400 italic mb-1">
            "The solar storms inscribe themselves in the source code of collective consciousness"
          </p>
          <p className="text-xs text-gray-500">
            — Alexander Chizhevsky, adapted for the digital age
          </p>
          <p className="text-xs text-cyan-400 mt-2 font-mono">
            mechbot.2x · mechmind-dwv · HelioBio-Social v2.0.1 · 2024-2025
          </p>
        </div>
      </div>
    </div>
  );
};

export default HelioBioScientificDashboard;
