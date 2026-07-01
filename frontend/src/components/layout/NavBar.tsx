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
    <nav className="fixed bottom-0 left-0 right-0 bg-cosmos-800 border-t border-cosmos-700 z-50">
      <div className="flex justify-around items-center h-16 max-w-md mx-auto">
        {navItems.map(({ path, icon: Icon, label }) => {
          const isActive = location.pathname === path;
          return (
            <button
              key={path}
              onClick={() => navigate(path)}
              className={`flex flex-col items-center justify-center gap-1 flex-1 h-full transition-colors ${
                isActive ? 'text-accent-blue' : 'text-text-secondary'
              }`}
            >
              <Icon className="w-6 h-6" />
              <span className="text-xs">{label}</span>
            </button>
          );
        })}
      </div>
    </nav>
  );
}
