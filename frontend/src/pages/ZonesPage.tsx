import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { getZones } from '../api/routes';
import type { Zone } from '../types';

export function ZonesPage() {
  const [zones, setZones] = useState<Zone[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getZones()
      .then(setZones)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="p-4 pb-28">
      <motion.header
        className="mb-5"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="font-display text-lg uppercase tracking-[0.2em] text-neon-purple">Галактика</h1>
        <p className="text-xs text-slate-500 mt-1">Выберите зону для экспедиции</p>
      </motion.header>

      {loading ? (
        <div className="glass-card p-8 text-center">
          <p className="text-slate-500 text-xs">Загрузка зон...</p>
        </div>
      ) : zones.length === 0 ? (
        <div className="glass-card p-8 text-center">
          <p className="text-slate-500 text-xs">Нет доступных зон</p>
        </div>
      ) : (
        <div className="flex flex-col gap-3">
          {zones.map((zone, i) => (
            <motion.div
              key={zone.id}
              className="glass-card p-4 cursor-pointer hover:border-neon-cyan/30 transition-all"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              onClick={() => alert(`Зона: ${zone.name}`)}
            >
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-display text-white">{zone.name}</h3>
                  <p className="text-[10px] text-slate-500 mt-1">{zone.description}</p>
                </div>
                <div className="text-right">
                  <div className="text-[10px] text-neon-cyan">⛽ {zone.fuel_cost}</div>
                  <div className="text-[10px] text-neon-amber">⏱ {zone.duration_seconds}с</div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}
