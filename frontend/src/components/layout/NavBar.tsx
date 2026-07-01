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
    <nav className="fixed bottom-0 left-0 right-0 z-50 bg-black/40 backdrop-blur-lg border-t border-white/10">
      <div className="flex justify-around items-center h-16 max-w-md mx-auto">
        {navItems.map(({ path, icon: Icon, label }) => {
          const isActive = location.pathname === path;
          return (
            <button
              key={path}
              onClick={() => navigate(path)}
              className="flex flex-col items-center justify-center gap-1 flex-1 h-full transition-all duration-200"
            >
              <Icon
                className={`transition-all duration-200 ${
                  isActive
                    ? 'w-7 h-7 text-[#1ADAFC] drop-shadow-[0_0_8px_#1ADAFC]'
                    : 'w-6 h-6 text-[#6b7280]'
                }`}
              />
              <span
                className={`text-[10px] transition-colors duration-200 ${
                  isActive ? 'text-[#1ADAFC]' : 'text-[#6b7280]'
                }`}
              >
                {label}
              </span>
            </button>
          );
        })}
      </div>
    </nav>
  );
}
