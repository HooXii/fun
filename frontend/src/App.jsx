import { Navigate, Route, Routes } from 'react-router-dom';

import { isAuthenticated } from './api/client.js';
import Layout from './components/Layout.jsx';
import DashboardPage from './pages/DashboardPage.jsx';
import DriversPage from './pages/DriversPage.jsx';
import ExpensesPage from './pages/ExpensesPage.jsx';
import FuelLogsPage from './pages/FuelLogsPage.jsx';
import LoginPage from './pages/LoginPage.jsx';
import MaintenancePage from './pages/MaintenancePage.jsx';
import OptimizationPage from './pages/OptimizationPage.jsx';
import ReportsPage from './pages/ReportsPage.jsx';
import RoutesPage from './pages/RoutesPage.jsx';
import TripsPage from './pages/TripsPage.jsx';
import VehiclesPage from './pages/VehiclesPage.jsx';

function ProtectedRoute({ children }) {
  if (!isAuthenticated()) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route index element={<DashboardPage />} />
        <Route path="vehicles" element={<VehiclesPage />} />
        <Route path="drivers" element={<DriversPage />} />
        <Route path="routes" element={<RoutesPage />} />
        <Route path="trips" element={<TripsPage />} />
        <Route path="expenses" element={<ExpensesPage />} />
        <Route path="fuel-logs" element={<FuelLogsPage />} />
        <Route path="maintenance" element={<MaintenancePage />} />
        <Route path="optimization" element={<OptimizationPage />} />
        <Route path="reports" element={<ReportsPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

