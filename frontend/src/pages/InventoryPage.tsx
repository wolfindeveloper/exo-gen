import { motion } from 'framer-motion';

export function InventoryPage() {
  return (
    <div className="p-4 pb-28">
      <motion.header
        className="mb-5"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="font-display text-lg uppercase tracking-[0.2em] text-neon-purple">Инвентарь</h1>
        <p className="text-xs text-slate-500 mt-1">Ваша коллекция космического хлама</p>
      </motion.header>

      <div className="glass-card p-8 text-center">
        <p className="text-slate-500 text-xs">Инвентарь пока пуст</p>
        <p className="text-[10px] text-slate-600 mt-2">Отправляйтесь в экспедицию, чтобы найти артефакты</p>
      </div>
    </div>
  );
}
