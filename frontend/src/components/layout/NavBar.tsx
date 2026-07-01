import { motion } from 'framer-motion';
import { Rocket, Map, Package, User } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';

const nav = [
  { path: '/', icon: Rocket, label: 'Ангар' },
  { path: '/zones', icon: Map, label: 'Карта' },
  { path: '/inventory', icon: Package, label: 'Инвентарь' },
  { path: '/profile', icon: User, label: 'Профиль' },
];

export function NavBar() {
  const location = useLocation();

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 backdrop-blur-[16px] border-t bg-space-900/80 border-white/[0.04]">
      <div className="flex max-w-lg mx-auto items-stretch">
        {nav.map((item) => {
          const active = location.pathname === item.path;
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex-1 flex flex-col items-center justify-center gap-0.5 py-2.5 relative transition-all ${
                active ? 'text-neon-cyan' : 'text-slate-600 hover:text-slate-400'
              }`}
            >
              {active && (
                <motion.span
                  layoutId="nav-active-bg"
                  className="absolute inset-x-2 inset-y-1 rounded-xl bg-white/[0.06] border border-white/[0.06]"
                  transition={{ type: 'spring', stiffness: 400, damping: 30 }}
                />
              )}
              {active && (
                <motion.span
                  layoutId="nav-active-bar"
                  className="absolute -top-px left-3 right-3 h-[2px] rounded-full bg-gradient-to-r from-neon-cyan/60 via-neon-cyan to-neon-cyan/60"
                  transition={{ type: 'spring', stiffness: 400, damping: 30 }}
                />
              )}
              <span className="relative">
                <item.icon
                  size={20}
                  strokeWidth={1.5}
                  className={`transition-all ${active ? 'text-neon-cyan drop-shadow-[0_0_6px_rgba(34,211,238,0.5)]' : 'text-slate-600'}`}
                />
              </span>
              <span className="font-display text-[10px] uppercase tracking-wider leading-none">
                {item.label}
              </span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
