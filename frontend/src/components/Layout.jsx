import {
  BarChart3,
  CarFront,
  ClipboardList,
  FileText,
  Fuel,
  LogOut,
  Map,
  Route,
  Settings2,
  Truck,
  UserRound,
  Wrench,
} from 'lucide-react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';

import { logout } from '../api/client.js';

const navItems = [
  { to: '/', label: 'Dashboard', icon: BarChart3 },
  { to: '/vehicles', label: 'Автомобили', icon: Truck },
  { to: '/drivers', label: 'Водители', icon: UserRound },
  { to: '/routes', label: 'Маршруты', icon: Route },
  { to: '/trips', label: 'Рейсы', icon: ClipboardList },
  { to: '/expenses', label: 'Расходы', icon: CarFront },
  { to: '/fuel-logs', label: 'Топливо', icon: Fuel },
  { to: '/maintenance', label: 'ТО', icon: Wrench },
  { to: '/optimization', label: 'Оптимизация', icon: Settings2 },
  { to: '/reports', label: 'Отчеты', icon: FileText },
];

export default function Layout() {
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate('/login');
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <Map size={24} />
          <div>
            <strong>TransportCost</strong>
            <span>учет расходов</span>
          </div>
        </div>
        <nav className="nav-list">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === '/'}
                className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
              >
                <Icon size={18} />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </nav>
        <button className="ghost-button sidebar-logout" type="button" onClick={handleLogout} title="Выйти">
          <LogOut size={18} />
          <span>Выйти</span>
        </button>
      </aside>
      <main className="content">
        <Outlet />
      </main>
    </div>
  );
}
