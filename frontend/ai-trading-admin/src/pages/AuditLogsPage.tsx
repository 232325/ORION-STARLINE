import { useState, useEffect } from 'react';
import { FileText, Filter, AlertTriangle, Shield, User, Settings } from 'lucide-react';
import { supabase } from '../lib/supabase';
import { useAuth } from '../contexts/AuthContext';

interface AuditLog {
  id: string;
  action_type: string;
  resource_type: string;
  resource_id: string | null;
  details: any;
  ip_address: string;
  user_agent: string;
  risk_level: string;
  is_suspicious: boolean;
  created_at: string;
}

export default function AuditLogsPage() {
  const { user } = useAuth();
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({
    action_type: '',
    resource_type: '',
  });
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    loadLogs();
  }, [user, filters]);

  const loadLogs = async () => {
    if (!user) return;

    setLoading(true);
    try {
      const queryParams = new URLSearchParams({
        user_id: user.id,
        limit: '50',
        offset: '0',
        ...filters,
      });

      const { data, error } = await supabase.functions.invoke('audit-logging', {
        method: 'GET',
        body: { user_id: user.id, ...filters },
      });

      if (error) throw error;
      setLogs(data.logs || []);
      setStats(data.stats);
    } catch (error) {
      console.error('Xatolik:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'low': return 'text-green-400';
      case 'medium': return 'text-yellow-400';
      case 'high': return 'text-red-400';
      default: return 'text-slate-400';
    }
  };

  const getRiskBadge = (level: string) => {
    switch (level) {
      case 'low': return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'medium': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      case 'high': return 'bg-red-500/20 text-red-400 border-red-500/30';
      default: return 'bg-slate-500/20 text-slate-400 border-slate-500/30';
    }
  };

  const getActionIcon = (actionType: string) => {
    if (actionType.includes('login')) return <User className="w-5 h-5" />;
    if (actionType.includes('trade')) return <Shield className="w-5 h-5" />;
    if (actionType.includes('settings')) return <Settings className="w-5 h-5" />;
    return <FileText className="w-5 h-5" />;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-orange-900 to-slate-900 p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-white mb-2 flex items-center gap-3">
          <FileText className="w-10 h-10 text-orange-400" />
          Audit Logs
        </h1>
        <p className="text-slate-400">Tizim va foydalanuvchi faoliyati jurnali</p>
      </div>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6">
            <p className="text-slate-400 text-sm mb-1">Oxirgi 24 soat</p>
            <p className="text-3xl font-bold text-white">{stats.last24h}</p>
          </div>
          <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6">
            <p className="text-slate-400 text-sm mb-1">Oxirgi 7 kun</p>
            <p className="text-3xl font-bold text-white">{stats.last7d}</p>
          </div>
          <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6">
            <p className="text-slate-400 text-sm mb-1">Shubhali harakatlar</p>
            <p className="text-3xl font-bold text-red-400">{stats.suspicious}</p>
          </div>
          <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6">
            <p className="text-slate-400 text-sm mb-1">Eng ko'p harakat</p>
            <p className="text-lg font-bold text-orange-400">
              {Object.keys(stats.byActionType).length > 0
                ? Object.entries(stats.byActionType).sort((a: any, b: any) => b[1] - a[1])[0][0]
                : 'N/A'}
            </p>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6 mb-6">
        <div className="flex items-center gap-3 mb-4">
          <Filter className="w-5 h-5 text-orange-400" />
          <h2 className="text-xl font-bold text-white">Filtrlar</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-slate-400 text-sm mb-2">Harakat turi</label>
            <select
              value={filters.action_type}
              onChange={(e) => setFilters({ ...filters, action_type: e.target.value })}
              className="w-full px-4 py-2 bg-slate-900/50 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-orange-500"
            >
              <option value="">Barchasi</option>
              <option value="login_attempt">Kirish urinishi</option>
              <option value="trade_executed">Trade bajarildi</option>
              <option value="settings_modified">Sozlamalar o'zgartirildi</option>
              <option value="password_changed">Parol o'zgartirildi</option>
              <option value="funds_withdrawn">Mablag' yechildi</option>
            </select>
          </div>

          <div>
            <label className="block text-slate-400 text-sm mb-2">Resurs turi</label>
            <select
              value={filters.resource_type}
              onChange={(e) => setFilters({ ...filters, resource_type: e.target.value })}
              className="w-full px-4 py-2 bg-slate-900/50 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-orange-500"
            >
              <option value="">Barchasi</option>
              <option value="user">Foydalanuvchi</option>
              <option value="trade">Trade</option>
              <option value="wallet">Hamyon</option>
              <option value="settings">Sozlamalar</option>
            </select>
          </div>

          <div className="flex items-end">
            <button
              onClick={loadLogs}
              disabled={loading}
              className="w-full px-6 py-2 bg-orange-600 hover:bg-orange-700 text-white rounded-lg transition-all disabled:opacity-50"
            >
              Qo'llash
            </button>
          </div>
        </div>
      </div>

      {/* Logs List */}
      <div className="space-y-3">
        {loading ? (
          <div className="text-center py-12">
            <FileText className="w-12 h-12 text-orange-400 animate-pulse mx-auto mb-4" />
            <p className="text-slate-400">Yuklanmoqda...</p>
          </div>
        ) : logs.length === 0 ? (
          <div className="text-center py-12 bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl">
            <FileText className="w-16 h-16 text-slate-600 mx-auto mb-4" />
            <p className="text-slate-400">Loglar topilmadi</p>
          </div>
        ) : (
          logs.map((log) => (
            <div
              key={log.id}
              className={`bg-slate-800/50 backdrop-blur border rounded-xl p-6 transition-all ${
                log.is_suspicious ? 'border-red-500/50' : 'border-slate-700 hover:border-orange-500/50'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-4 flex-1">
                  <div className={`p-3 rounded-lg ${
                    log.is_suspicious ? 'bg-red-500/20' : 'bg-orange-500/20'
                  }`}>
                    {getActionIcon(log.action_type)}
                  </div>

                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-white font-semibold text-lg">{log.action_type}</h3>
                      <span className={`px-3 py-1 rounded-lg border text-xs font-medium ${getRiskBadge(log.risk_level)}`}>
                        {log.risk_level.toUpperCase()}
                      </span>
                      {log.is_suspicious && (
                        <span className="px-3 py-1 bg-red-500/20 text-red-400 border border-red-500/30 rounded-lg text-xs font-medium flex items-center gap-1">
                          <AlertTriangle className="w-3 h-3" />
                          SHUBHALI
                        </span>
                      )}
                    </div>

                    <div className="flex items-center gap-4 text-sm text-slate-400 mb-3">
                      <span>Resurs: {log.resource_type}</span>
                      {log.resource_id && (
                        <>
                          <span>•</span>
                          <span>ID: {log.resource_id}</span>
                        </>
                      )}
                      <span>•</span>
                      <span>{new Date(log.created_at).toLocaleString('uz')}</span>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                      <div className="p-3 bg-slate-900/50 rounded-lg">
                        <p className="text-slate-400 mb-1">IP Address</p>
                        <p className="text-white font-mono">{log.ip_address}</p>
                      </div>
                      <div className="p-3 bg-slate-900/50 rounded-lg">
                        <p className="text-slate-400 mb-1">User Agent</p>
                        <p className="text-white truncate">{log.user_agent}</p>
                      </div>
                    </div>

                    {log.details && (
                      <details className="mt-3">
                        <summary className="cursor-pointer text-orange-400 text-sm hover:text-orange-300">
                          Batafsil ma'lumot
                        </summary>
                        <pre className="mt-2 p-3 bg-slate-900/50 rounded-lg text-xs text-slate-300 overflow-x-auto">
                          {JSON.stringify(log.details, null, 2)}
                        </pre>
                      </details>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
