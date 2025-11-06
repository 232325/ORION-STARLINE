import { useEffect, useState } from 'react';
import { supabase } from '../lib/supabase';

interface User {
  id: string;
  user_id: string;
  email: string;
  full_name: string;
  role: string;
  balance: number;
  created_at: string;
}

export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadUsers();
  }, []);

  async function loadUsers() {
    try {
      const { data } = await supabase
        .from('profiles')
        .select('*')
        .order('created_at', { ascending: false });

      setUsers(data || []);
    } catch (error) {
      console.error('Error loading users:', error);
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
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-white mb-2">Foydalanuvchilar</h2>
          <p className="text-slate-400">Barcha foydalanuvchilarni boshqaring</p>
        </div>
      </div>

      <div className="bg-slate-800/50 backdrop-blur-xl rounded-xl border border-slate-700 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-slate-700/50">
              <tr>
                <th className="text-left py-4 px-6 text-slate-300 font-semibold">Email</th>
                <th className="text-left py-4 px-6 text-slate-300 font-semibold">Ism</th>
                <th className="text-left py-4 px-6 text-slate-300 font-semibold">Rol</th>
                <th className="text-left py-4 px-6 text-slate-300 font-semibold">Balans</th>
                <th className="text-left py-4 px-6 text-slate-300 font-semibold">Ro'yxatdan o'tgan</th>
              </tr>
            </thead>
            <tbody>
              {users.length === 0 ? (
                <tr>
                  <td colSpan={5} className="text-center py-12 text-slate-400">
                    Foydalanuvchilar topilmadi
                  </td>
                </tr>
              ) : (
                users.map((user) => (
                  <tr key={user.id} className="border-b border-slate-700/50 hover:bg-slate-700/30 transition-colors">
                    <td className="py-4 px-6 text-white">{user.email}</td>
                    <td className="py-4 px-6 text-slate-300">{user.full_name || '-'}</td>
                    <td className="py-4 px-6">
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                        user.role === 'admin'
                          ? 'bg-purple-500/20 text-purple-400'
                          : 'bg-blue-500/20 text-blue-400'
                      }`}>
                        {user.role?.toUpperCase() || 'USER'}
                      </span>
                    </td>
                    <td className="py-4 px-6 text-slate-300">
                      ${(user.balance || 0).toLocaleString()}
                    </td>
                    <td className="py-4 px-6 text-slate-400">
                      {new Date(user.created_at).toLocaleDateString('uz-UZ')}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
