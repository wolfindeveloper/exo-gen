import { useLocation, useNavigate } from 'react-router-dom';
import { Rocket, Map, Backpack, User } from 'lucide-react';

const navItems = [
  { path: '/', icon: Rocket, label: 'Корабль' },
  { path: '/zones', icon: Map, label: 'Зоны' },
  { path: '/inventory', icon: Backpack, label: 'Рюкзак' },
  { path: '/profile', icon: User, label: 'Профиль' },
] as const;

export function NavBar() {
  const location = useLocation();
  const navigate = useNavigate();

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50">
      <div className="glass-panel border-t-0 rounded-t-2xl max-w-md mx-auto">
        <div className="flex justify-around items-center py-3">
          {navItems.map(({ path, icon: Icon, label }) => {
            const isActive = location.pathname === path;
            return (
              <button
                key={path}
                onClick={() => navigate(path)}
                className="flex flex-col items-center justify-center gap-1 flex-1 transition-all duration-300 relative"
              >
                <Icon
                  className={`transition-all duration-300 ${
                    isActive
                      ? 'w-7 h-7 neon-text-cyan'
                      : 'w-6 h-6 text-gray-500'
                  }`}
                />
                <span
                  className={`text-[10px] font-medium transition-all duration-300 ${
                    isActive ? 'neon-text-cyan' : 'text-gray-500'
                  }`}
                >
                  {label}
                </span>
                {isActive && (
                  <div className="absolute -bottom-1 w-1.5 h-1.5 rounded-full bg-cyan-400 shadow-[0_0_8px_rgba(26,218,252,0.8)] animate-pulse-glow" />
                )}
              </button>
            );
          })}
        </div>
      </div>
    </nav>
  );
}
