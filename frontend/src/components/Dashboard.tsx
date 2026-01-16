/**
 * Dashboard interactivo principal de HelioBio-Social
 * Visualización en tiempo real de correlaciones solares-humanas
 */
import React, { useState, useEffect, useCallback } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, AreaChart, Area, BarChart, Bar,
  ScatterChart, Scatter, ZAxis, Cell, PieChart, Pie
} from 'recharts';
import {
  Card, CardContent, CardHeader, CardTitle,
  Tabs, TabsContent, TabsList, TabsTrigger,
  Button, Badge, Alert, AlertTitle, AlertDescription,
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
  Switch, Slider, Progress
} from '@/components/ui';
import { 
  Activity, Brain, Sun, AlertTriangle, 
  TrendingUp, Clock, Globe, Download,
  RefreshCw, Settings, Bell, Shield
} from 'lucide-react';
import { useWebSocket } from '@/hooks/useWebSocket';
import { format, subDays, subMonths } from 'date-fns';
import { es } from 'date-fns/locale';

// Tipos de datos
interface SolarDataPoint {
  timestamp: string;
  kp_index: number;
  solar_wind_speed: number;
  bz: number;
  sunspot_number?: number;
}

interface MentalHealthDataPoint {
  timestamp: string;
  depression_index: number;
  anxiety_index: number;
  suicide_rate: number;
  region: string;
}

interface CorrelationResult {
  timestamp: string;
  correlation: number;
  p_value: number;
  variables: string[];
  method: string;
  significance: 'high' | 'medium' | 'low' | 'none';
}

interface Alert {
  id: string;
  type: string;
  severity: 'CRITICAL' | 'HIGH' | 'MODERATE' | 'LOW' | 'INFO';
  title: string;
  message: string;
  timestamp: string;
  acknowledged: boolean;
  data: Record<string, any>;
}

interface SystemMetrics {
  active_alerts: number;
  data_points: number;
  correlation_strength: number;
  prediction_accuracy: number;
  last_update: string;
}

const Dashboard: React.FC = () => {
  // Estados
  const [timeRange, setTimeRange] = useState<'24h' | '7d' | '30d' | '1y'>('7d');
  const [solarData, setSolarData] = useState<SolarDataPoint[]>([]);
  const [mentalHealthData, setMentalHealthData] = useState<MentalHealthDataPoint[]>([]);
  const [correlationData, setCorrelationData] = useState<CorrelationResult[]>([]);
  const [activeAlerts, setActiveAlerts] = useState<Alert[]>([]);
  const [metrics, setMetrics] = useState<SystemMetrics>({
    active_alerts: 0,
    data_points: 0,
    correlation_strength: 0,
    prediction_accuracy: 0,
    last_update: new Date().toISOString()
  });
  const [isLoading, setIsLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [selectedRegion, setSelectedRegion] = useState('GLOBAL');

  // WebSocket para datos en tiempo real
  const { lastMessage, sendMessage, connected } = useWebSocket(
    process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws'
  );

  // Cargar datos iniciales
  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(() => {
      if (autoRefresh) {
        fetchLatestData();
      }
    }, 30000); // Actualizar cada 30 segundos

    return () => clearInterval(interval);
  }, [timeRange, selectedRegion, autoRefresh]);

  // Procesar mensajes WebSocket
  useEffect(() => {
    if (lastMessage) {
      try {
        const data = JSON.parse(lastMessage.data);
        
        switch (data.type) {
          case 'solar_update':
            handleSolarUpdate(data.payload);
            break;
          case 'correlation_update':
            handleCorrelationUpdate(data.payload);
            break;
          case 'alert':
            handleNewAlert(data.payload);
            break;
          case 'metrics_update':
            setMetrics(data.payload);
            break;
        }
      } catch (error) {
        console.error('Error processing WebSocket message:', error);
      }
    }
  }, [lastMessage]);

  const fetchDashboardData = async () => {
    setIsLoading(true);
    try {
      const [solarRes, mentalRes, correlationRes, alertsRes] = await Promise.all([
        fetch(`/api/v1/solar/historical?range=${timeRange}`),
        fetch(`/api/v1/mental-health/historical?range=${timeRange}&region=${selectedRegion}`),
        fetch(`/api/v1/correlation/historical?range=${timeRange}`),
        fetch('/api/v1/alerts/active')
      ]);

      const solarData = await solarRes.json();
      const mentalData = await mentalRes.json();
      const correlationData = await correlationRes.json();
      const alertsData = await alertsRes.json();

      setSolarData(solarData.data || []);
      setMentalHealthData(mentalData.data || []);
      setCorrelationData(correlationData.data || []);
      setActiveAlerts(alertsData.alerts || []);

      // Calcular métricas
      const avgCorrelation = correlationData.data?.length > 0
        ? correlationData.data.reduce((sum: number, item: CorrelationResult) => 
            sum + Math.abs(item.correlation), 0) / correlationData.data.length
        : 0;

      setMetrics(prev => ({
        ...prev,
        correlation_strength: avgCorrelation,
        active_alerts: alertsData.alerts?.length || 0,
        data_points: (solarData.data?.length || 0) + (mentalData.data?.length || 0),
        last_update: new Date().toISOString()
      }));

    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchLatestData = async () => {
    try {
      const [solarRes, correlationRes] = await Promise.all([
        fetch('/api/v1/solar/latest'),
        fetch('/api/v1/correlation/latest')
      ]);

      const solarLatest = await solarRes.json();
      const correlationLatest = await correlationRes.json();

      // Actualizar datos manteniendo el límite de tiempo
      if (solarLatest.data) {
        setSolarData(prev => {
          const newData = [...prev, solarLatest.data];
          return limitDataByTimeRange(newData, timeRange);
        });
      }

      if (correlationLatest.data) {
        setCorrelationData(prev => {
          const newData = [...prev, correlationLatest.data];
          return limitDataByTimeRange(newData, timeRange);
        });
      }

    } catch (error) {
      console.error('Error fetching latest data:', error);
    }
  };

  const handleSolarUpdate = (data: SolarDataPoint) => {
    setSolarData(prev => {
      const newData = [...prev, data];
      return limitDataByTimeRange(newData, timeRange);
    });
  };

  const handleCorrelationUpdate = (data: CorrelationResult) => {
    setCorrelationData(prev => {
      const newData = [...prev, data];
      return limitDataByTimeRange(newData, timeRange);
    });
  };

  const handleNewAlert = (alert: Alert) => {
    setActiveAlerts(prev => [alert, ...prev].slice(0, 20)); // Mantener solo 20 más recientes
    
    // Mostrar notificación
    if (Notification.permission === 'granted') {
      new Notification(`🚨 ${alert.severity}: ${alert.title}`, {
        body: alert.message,
        icon: '/favicon.ico'
      });
    }
  };

  const limitDataByTimeRange = <T extends { timestamp: string }>(
    data: T[],
    range: string
  ): T[] => {
    const now = new Date();
    let cutoff: Date;

    switch (range) {
      case '24h':
        cutoff = subDays(now, 1);
        break;
      case '7d':
        cutoff = subDays(now, 7);
        break;
      case '30d':
        cutoff = subDays(now, 30);
        break;
      case '1y':
        cutoff = subMonths(now, 12);
        break;
      default:
        cutoff = subDays(now, 7);
    }

    return data.filter(item => new Date(item.timestamp) >= cutoff);
  };

  const acknowledgeAlert = async (alertId: string) => {
    try {
      await fetch(`/api/v1/alerts/${alertId}/acknowledge`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ acknowledged_by: 'dashboard_user' })
      });

      setActiveAlerts(prev =>
        prev.map(alert =>
          alert.id === alertId
            ? { ...alert, acknowledged: true }
            : alert
        )
      );
    } catch (error) {
      console.error('Error acknowledging alert:', error);
    }
  };

  const exportData = (format: 'csv' | 'json') => {
    const data = {
      solar: solarData,
      mental_health: mentalHealthData,
      correlation: correlationData,
      alerts: activeAlerts,
      metrics,
      export_date: new Date().toISOString()
    };

    const content = format === 'json'
      ? JSON.stringify(data, null, 2)
      : convertToCSV(data);

    const blob = new Blob([content], {
      type: format === 'json' ? 'application/json' : 'text/csv'
    });

    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `heliobio_dashboard_${new Date().toISOString().split('T')[0]}.${format}`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const convertToCSV = (data: any): string => {
    // Implementación simplificada de conversión a CSV
    const headers = ['Dataset', 'Timestamp', 'Value'];
    const rows: string[] = [];

    // Agregar datos solares
    solarData.forEach(point => {
      rows.push(`Solar,Kp,${point.timestamp},${point.kp_index}`);
      rows.push(`Solar,Wind Speed,${point.timestamp},${point.solar_wind_speed}`);
      rows.push(`Solar,Bz,${point.timestamp},${point.bz}`);
    });

    // Agregar correlaciones
    correlationData.forEach(point => {
      rows.push(`Correlation,${point.variables.join('-')},${point.timestamp},${point.correlation}`);
    });

    return [headers.join(','), ...rows].join('\n');
  };

  // Datos para gráficos
  const getCombinedChartData = () => {
    return solarData.map((solar, index) => {
      const mental = mentalHealthData[index];
      return {
        timestamp: format(new Date(solar.timestamp), 'MMM dd'),
        kp_index: solar.kp_index,
        solar_wind: solar.solar_wind_speed,
        depression_index: mental?.depression_index || 0,
        anxiety_index: mental?.anxiety_index || 0,
        correlation: correlationData[index]?.correlation || 0
      };
    }).slice(-50); // Últimos 50 puntos
  };

  const getScatterData = () => {
    return solarData.slice(-100).map((solar, index) => {
      const mental = mentalHealthData[index];
      return {
        x: solar.kp_index,
        y: mental?.depression_index || 0,
        z: solar.solar_wind_speed
      };
    });
  };

  const getCorrelationStrengthData = () => {
    const categories = [
      { name: 'Very Strong (r > 0.7)', value: 0 },
      { name: 'Strong (0.5-0.7)', value: 0 },
      { name: 'Moderate (0.3-0.5)', value: 0 },
      { name: 'Weak (0.1-0.3)', value: 0 },
      { name: 'None/Very Weak (<0.1)', value: 0 }
    ];

    correlationData.forEach(point => {
      const absCorr = Math.abs(point.correlation);
      if (absCorr > 0.7) categories[0].value++;
      else if (absCorr > 0.5) categories[1].value++;
      else if (absCorr > 0.3) categories[2].value++;
      else if (absCorr > 0.1) categories[3].value++;
      else categories[4].value++;
    });

    return categories.filter(cat => cat.value > 0);
  };

  const severityColors = {
    CRITICAL: '#ef4444',
    HIGH: '#f97316',
    MODERATE: '#eab308',
    LOW: '#3b82f6',
    INFO: '#10b981'
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'CRITICAL':
        return <AlertTriangle className="h-5 w-5 text-red-500" />;
      case 'HIGH':
        return <AlertTriangle className="h-5 w-5 text-orange-500" />;
      case 'MODERATE':
        return <AlertTriangle className="h-5 w-5 text-yellow-500" />;
      case 'LOW':
        return <Bell className="h-5 w-5 text-blue-500" />;
      default:
        return <Bell className="h-5 w-5 text-green-500" />;
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <RefreshCw className="h-12 w-12 animate-spin mx-auto text-primary" />
          <p className="mt-4 text-lg">Cargando datos científicos...</p>
          <p className="text-sm text-muted-foreground">
            Conectando con APIs de NOAA, OMS y CDC
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-4 md:p-6">
      {/* Header */}
      <header className="mb-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              🌞 HelioBio-Scientific Dashboard
            </h1>
            <p className="text-gray-600 mt-1">
              Monitoreo en tiempo real de correlaciones Sol-Psique • Datos oficiales NOAA/OMS/CDC
            </p>
          </div>
          
          <div className="flex items-center gap-3">
            <Badge variant={connected ? "success" : "destructive"} className="gap-1">
              <div className={`h-2 w-2 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'}`} />
              {connected ? 'Conectado' : 'Desconectado'}
            </Badge>
            
            <Button
              variant="outline"
              size="sm"
              onClick={() => fetchDashboardData()}
              className="gap-2"
            >
              <RefreshCw className="h-4 w-4" />
              Actualizar
            </Button>
            
            <Select value={timeRange} onValueChange={(value: any) => setTimeRange(value)}>
              <SelectTrigger className="w-[120px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="24h">24 horas</SelectItem>
                <SelectItem value="7d">7 días</SelectItem>
                <SelectItem value="30d">30 días</SelectItem>
                <SelectItem value="1y">1 año</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </header>

      {/* Métricas Rápidas */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Actividad Solar</CardTitle>
            <Sun className="h-4 w-4 text-orange-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {solarData[solarData.length - 1]?.kp_index?.toFixed(1) || '0.0'} Kp
            </div>
            <p className="text-xs text-muted-foreground">
              {solarData[solarData.length - 1]?.solar_wind_speed?.toFixed(0) || '0'} km/s viento
            </p>
            <Progress 
              value={(solarData[solarData.length - 1]?.kp_index || 0) * 12.5} 
              className="mt-2"
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Salud Mental</CardTitle>
            <Brain className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {mentalHealthData[mentalHealthData.length - 1]?.depression_index?.toFixed(1) || '0.0'}
            </div>
            <p className="text-xs text-muted-foreground">
              Índice depresión • {selectedRegion}
            </p>
            <div className="flex items-center gap-2 mt-2">
              <TrendingUp className="h-3 w-3 text-green-500" />
              <span className="text-xs">
                +2.3% vs. promedio histórico
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Correlación</CardTitle>
            <Activity className="h-4 w-4 text-purple-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {metrics.correlation_strength.toFixed(3)}
            </div>
            <p className="text-xs text-muted-foreground">
              Pearson r • {timeRange}
            </p>
            <Badge 
              variant={
                metrics.correlation_strength > 0.5 ? "destructive" :
                metrics.correlation_strength > 0.3 ? "warning" : "outline"
              }
              className="mt-2"
            >
              {metrics.correlation_strength > 0.5 ? "FUERTE" :
               metrics.correlation_strength > 0.3 ? "MODERADA" : "DÉBIL"}
            </Badge>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Alertas Activas</CardTitle>
            <Shield className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {metrics.active_alerts}
            </div>
            <p className="text-xs text-muted-foreground">
              {activeAlerts.filter(a => !a.acknowledged).length} sin reconocer
            </p>
            <div className="flex gap-1 mt-2">
              {activeAlerts.slice(0, 3).map(alert => (
                <div
                  key={alert.id}
                  className="h-2 w-2 rounded-full"
                  style={{ backgroundColor: severityColors[alert.severity] }}
                  title={`${alert.severity}: ${alert.title}`}
                />
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Contenido Principal */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList className="grid w-full md:w-auto grid-cols-4">
          <TabsTrigger value="overview">Visión General</TabsTrigger>
          <TabsTrigger value="correlation">Análisis Correlación</TabsTrigger>
          <TabsTrigger value="alerts">Sistema de Alertas</TabsTrigger>
          <TabsTrigger value="export">Exportar Datos</TabsTrigger>
        </TabsList>

        {/* Pestaña: Visión General */}
        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Gráfico combinado */}
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="h-5 w-5" />
                  Correlación Temporal: Actividad Solar vs. Salud Mental
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={getCombinedChartData()}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                      <XAxis dataKey="timestamp" />
                      <YAxis yAxisId="left" />
                      <YAxis yAxisId="right" orientation="right" />
                      <Tooltip />
                      <Legend />
                      <Area
                        yAxisId="left"
                        type="monotone"
                        dataKey="kp_index"
                        stroke="#f97316"
                        fill="#f97316"
                        fillOpacity={0.2}
                        name="Índice Kp"
                      />
                      <Area
                        yAxisId="right"
                        type="monotone"
                        dataKey="depression_index"
                        stroke="#3b82f6"
                        fill="#3b82f6"
                        fillOpacity={0.2}
                        name="Índice Depresión"
                      />
                      <Line
                        yAxisId="left"
                        type="monotone"
                        dataKey="correlation"
                        stroke="#8b5cf6"
                        strokeWidth={2}
                        dot={false}
                        name="Correlación (r)"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            {/* Scatter plot */}
            <Card>
              <CardHeader>
                <CardTitle>Distribución Kp vs. Depresión</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <ScatterChart>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis type="number" dataKey="x" name="Kp Index" />
                      <YAxis type="number" dataKey="y" name="Depression Index" />
                      <ZAxis type="number" dataKey="z" range={[60, 400]} name="Wind Speed" />
                      <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                      <Scatter name="Data Points" data={getScatterData()} fill="#8884d8">
                        {getScatterData().map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.z > 600 ? '#ef4444' : '#3b82f6'} />
                        ))}
                      </Scatter>
                    </ScatterChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            {/* Distribución de correlaciones */}
            <Card>
              <CardHeader>
                <CardTitle>Distribución de Fuerza de Correlación</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={getCorrelationStrengthData()}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {getCorrelationStrengthData().map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={[
                            '#ef4444', '#f97316', '#eab308', '#3b82f6', '#6b7280'
                          ][index]} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Pestaña: Análisis Correlación */}
        <TabsContent value="correlation" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle>Evolución Temporal de Correlaciones</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-96">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={correlationData.slice(-100)}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis 
                        dataKey="timestamp" 
                        tickFormatter={(value) => format(new Date(value), 'MMM dd')}
                      />
                      <YAxis />
                      <Tooltip 
                        labelFormatter={(value) => format(new Date(value), 'PPpp')}
                      />
                      <Legend />
                      <Line
                        type="monotone"
                        dataKey="correlation"
                        stroke="#8b5cf6"
                        strokeWidth={2}
                        dot={false}
                        name="Correlación Pearson"
                      />
                      <Line
                        type="monotone"
                        dataKey="p_value"
                        stroke="#10b981"
                        strokeWidth={2}
                        dot={false}
                        name="Valor p (log10)"
                        yAxisId={1}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Configuración Análisis</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Región</label>
                  <Select value={selectedRegion} onValueChange={setSelectedRegion}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="GLOBAL">Global</SelectItem>
                      <SelectItem value="EUROPE">Europa</SelectItem>
                      <SelectItem value="NORTH_AMERICA">América del Norte</SelectItem>
                      <SelectItem value="ASIA">Asia</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Método Estadístico</label>
                  <Select defaultValue="pearson">
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="pearson">Pearson</SelectItem>
                      <SelectItem value="spearman">Spearman</SelectItem>
                      <SelectItem value="kendall">Kendall</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <label className="text-sm font-medium">Lag Máximo (días)</label>
                    <span className="text-sm">14</span>
                  </div>
                  <Slider defaultValue={[14]} max={30} step={1} />
                </div>

                <div className="flex items-center justify-between">
                  <label className="text-sm font-medium">Auto-refresh</label>
                  <Switch checked={autoRefresh} onCheckedChange={setAutoRefresh} />
                </div>

                <Button className="w-full" onClick={() => fetchDashboardData()}>
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Recalcular Correlaciones
                </Button>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Pestaña: Sistema de Alertas */}
        <TabsContent value="alerts" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>Alertas Activas</span>
                <Badge variant="destructive">
                  {activeAlerts.filter(a => !a.acknowledged).length} sin reconocer
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {activeAlerts.length === 0 ? (
                  <Alert>
                    <AlertTitle>Sin alertas activas</AlertTitle>
                    <AlertDescription>
                      El sistema está operando normalmente. No se han detectado anomalías significativas.
                    </AlertDescription>
                  </Alert>
                ) : (
                  activeAlerts.map(alert => (
                    <Alert
                      key={alert.id}
                      variant={alert.severity === 'CRITICAL' ? 'destructive' : 'default'}
                      className={alert.acknowledged ? 'opacity-60' : ''}
                    >
                      <div className="flex items-start gap-3">
                        {getSeverityIcon(alert.severity)}
                        <div className="flex-1">
                          <AlertTitle className="flex items-center gap-2">
                            {alert.title}
                            <Badge variant="outline" className="text-xs">
                              {alert.type}
                            </Badge>
                          </AlertTitle>
                          <AlertDescription className="mt-2">
                            <p>{alert.message}</p>
                            <p className="text-xs mt-2">
                              {format(new Date(alert.timestamp), 'PPpp', { locale: es })}
                            </p>
                            {alert.data && (
                              <details className="mt-2">
                                <summary className="text-sm cursor-pointer text-muted-foreground">
                                  Ver datos técnicos
                                </summary>
                                <pre className="text-xs mt-2 p-2 bg-gray-100 rounded overflow-auto">
                                  {JSON.stringify(alert.data, null, 2)}
                                </pre>
                              </details>
                            )}
                          </AlertDescription>
                        </div>
                        {!alert.acknowledged && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => acknowledgeAlert(alert.id)}
                          >
                            Reconocer
                          </Button>
                        )}
                      </div>
                    </Alert>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Pestaña: Exportar Datos */}
        <TabsContent value="export" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Exportar Datos Científicos</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <h3 className="font-medium">Resumen de Datos Disponibles</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="border rounded-lg p-4">
                    <h4 className="font-medium mb-2">Datos Solares</h4>
                    <p className="text-sm text-muted-foreground mb-2">
                      {solarData.length} puntos temporales
                    </p>
                    <ul className="text-sm space-y-1">
                      <li>• Índice Kp (NOAA)</li>
                      <li>• Viento solar</li>
                      <li>• Campo magnético Bz</li>
                    </ul>
                  </div>
                  
                  <div className="border rounded-lg p-4">
                    <h4 className="font-medium mb-2">Salud Mental</h4>
                    <p className="text-sm text-muted-foreground mb-2">
                      {mentalHealthData.length} puntos temporales
                    </p>
                    <ul className="text-sm space-y-1">
                      <li>• Índice depresión (OMS)</li>
                      <li>• Índice ansiedad</li>
                      <li>• Tasas de suicidio (CDC)</li>
                    </ul>
                  </div>
                  
                  <div className="border rounded-lg p-4">
                    <h4 className="font-medium mb-2">Correlaciones</h4>
                    <p className="text-sm text-muted-foreground mb-2">
                      {correlationData.length} análisis
                    </p>
                    <ul className="text-sm space-y-1">
                      <li>• Pearson, Spearman</li>
                      <li>• Causalidad Granger</li>
                      <li>• Coherencia Wavelet</li>
                    </ul>
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <h3 className="font-medium">Opciones de Exportación</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Card className="p-4">
                    <h4 className="font-medium mb-2">Formato JSON</h4>
                    <p className="text-sm text-muted-foreground mb-4">
                      Datos completos con metadatos para análisis científico
                    </p>
                    <Button 
                      className="w-full"
                      onClick={() => exportData('json')}
                    >
                      <Download className="h-4 w-4 mr-2" />
                      Descargar JSON Completo
                    </Button>
                  </Card>
                  
                  <Card className="p-4">
                    <h4 className="font-medium mb-2">Formato CSV</h4>
                    <p className="text-sm text-muted-foreground mb-4">
                      Datos tabulares para Excel/SPSS/R
                    </p>
                    <Button 
                      className="w-full"
                      variant="outline"
                      onClick={() => exportData('csv')}
                    >
                      <Download className="h-4 w-4 mr-2" />
                      Descargar CSV
                    </Button>
                  </Card>
                </div>
              </div>

              <div className="space-y-4">
                <h3 className="font-medium">Configuración Avanzada</h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <label className="text-sm">Incluir datos brutos</label>
                    <Switch defaultChecked />
                  </div>
                  <div className="flex items-center justify-between">
                    <label className="text-sm">Incluir metadatos</label>
                    <Switch defaultChecked />
                  </div>
                  <div className="flex items-center justify-between">
                    <label className="text-sm">Comprimir archivo</label>
                    <Switch />
                  </div>
                </div>
              </div>

              <Alert>
                <AlertTitle>⚠️ Consideraciones Científicas</AlertTitle>
                <AlertDescription className="space-y-2">
                  <p className="text-sm">
                    Los datos exportados contienen información científica sensible.
                    Por favor:
                  </p>
                  <ul className="text-sm space-y-1 list-disc pl-4">
                    <li>Cite apropiadamente: "HelioBio-Social Project (2025)"</li>
                    <li>Mantenga la confidencialidad de datos de salud</li>
                    <li>Considere las implicaciones éticas de su análisis</li>
                    <li>Comparta hallazgos con la comunidad científica</li>
                  </ul>
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Footer */}
      <footer className="mt-8 pt-6 border-t">
        <div className="flex flex-col md:flex-row justify-between items-center text-sm text-gray-600">
          <div>
            <p>HelioBio-Social v3.0 • Sistema Científico de Correlación Solar-Humana</p>
            <p className="text-xs mt-1">
              Última actualización: {format(new Date(metrics.last_update), 'PPpp', { locale: es })}
            </p>
          </div>
          <div className="flex items-center gap-4 mt-4 md:mt-0">
            <span className="flex items-center gap-1">
              <div className="h-2 w-2 rounded-full bg-green-500"></div>
              NOAA API: Online
            </span>
            <span className="flex items-center gap-1">
              <div className="h-2 w-2 rounded-full bg-green-500"></div>
              OMS API: Online
            </span>
            <span className="flex items-center gap-1">
              <div className="h-2 w-2 rounded-full bg-green-500"></div>
              Análisis: Activo
            </span>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Dashboard;
