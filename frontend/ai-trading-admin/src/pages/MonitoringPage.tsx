import { useEffect, useState } from 'react';
import { supabase } from '../lib/supabase';
import { ComputerDesktopIcon } from '@heroicons/react/24/outline';

interface SystemLog {
  id: string;
  level: string;
  message: string;
  details: any;
  created_at: string;
}

interface SystemStats {
  total_positions: number;
  active_strategies: number;
  unread_alerts: number;
  recent_logs: SystemLog[];
  server_health: {
    status: string;
    uptime: string;
    cpu_usage: number;
    memory_usage: number;
  };
}

export default function MonitoringPage() {
  const [stats, setStats] = useState<SystemStats | null>(null);
  const [logs, setLogs] = useState<SystemLog[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadMonitoringData();
    const interval = setInterval(loadMonitoringData, 10000);
    return () => clearInterval(interval);
  }, []);

  async function loadMonitoringData() {
    try {
      const response = await supabase.functions.invoke('get-system-stats');
      
      if (response.data?.data) {
        setStats(response.data.data);
        setLogs(response.data.data.recent_logs || []);
      }
    } catch (error) {
      console.error('Error loading monitoring data:', error);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-white">Yuklanmoqda...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-white mb-2">System Monitoring</h2>
        <p className="text-slate-400">Tizim salomatligi va real-time loglar</p>
      </div>

      {stats && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-slate-800/50 backdrop-blur-xl rounded-xl border border-slate-700 p-6">
              <div className="flex items-center space-x-3 mb-3">
                <div className="p-2 bg-green-600/20 rounded-lg">
                  <ComputerDesktopIcon className="w-6 h-6 text-green-400" />
                </div>
                <p className="text-slate-400 text-sm">Server Status</p>
              </div>
              <p className="text-2xl font-bold text-green-400">{stats.server_health.status}</p>
              <p className="text-slate-400 text-sm mt-1">Uptime: {stats.server_health.uptime}</p>
            </div>

            <div className="bg-slate-800/50 backdrop-blur-xl rounded-xl border border-slate-700 p-6">
              <p className="text-slate-400 text-sm mb-3">CPU Usage</p>
              <p className="text-2xl font-bold text-white">{stats.server_health.cpu_usage.toFixed(1)}%</p>
              <div className="mt-3 bg-slate-700 rounded-full h-2 overflow-hidden">
                <div 
                  className="bg-blue-500 h-full transition-all"
                  style={{ width: `${stats.server_health.cpu_usage}%` }}
                ></div>
              </div>
            </div>

            <div className="bg-slate-800/50 backdrop-blur-xl rounded-xl border border-slate-700 p-6">
              <p className="text-slate-400 text-sm mb-3">Memory Usage</p>
              <p className="text-2xl font-bold text-white">{stats.server_health.memory_usage.toFixed(1)}%</p>
              <div className="mt-3 bg-slate-700 rounded-full h-2 overflow-hidden">
                <div 
                  className="bg-purple-500 h-full transition-all"
                  style={{ width: `${stats.server_health.memory_usage}%` }}
                ></div>
              </div>
            </div>

            <div className="bg-slate-800/50 backdrop-blur-xl rounded-xl border border-slate-700 p-6">
              <p className="text-slate-400 text-sm mb-3">O'qilmagan Alerts</p>
              <p className="text-2xl font-bold text-red-400">{stats.unread_alerts}</p>
            </div>
          </div>

          <div className="bg-slate-800/50 backdrop-blur-xl rounded-xl border border-slate-700 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold text-white">Real-time System Logs</h3>
              <span className="px-3 py-1 bg-green-500/20 text-green-400 text-xs font-semibold rounded-full">
                LIVE
              </span>
            </div>
            <div className="space-y-2 max-h-[500px] overflow-y-auto">
              {logs.length === 0 ? (
                <p className="text-center py-8 text-slate-400">Loglar topilmadi</p>
              ) : (
                logs.map((log) => (
                  <div
                    key={log.id}
                    className="flex items-start space-x-3 p-3 bg-slate-700/30 rounded-lg hover:bg-slate-700/50 transition-colors"
                  >
                    <span className={`mt-1 px-2 py-1 rounded text-xs font-semibold ${
                      log.level === 'error'
                        ? 'bg-red-500/20 text-red-400'
                        : log.level === 'warning'
                        ? 'bg-yellow-500/20 text-yellow-400'
                        : 'bg-blue-500/20 text-blue-400'
                    }`}>
                      {log.level.toUpperCase()}
                    </span>
                    <div className="flex-1">
                      <p className="text-white text-sm">{log.message}</p>
                      <p className="text-slate-400 text-xs mt-1">
                        {new Date(log.created_at).toLocaleString('uz-UZ')}
                      </p>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
