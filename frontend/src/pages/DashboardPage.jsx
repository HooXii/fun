import { Activity, CircleDollarSign, Route, Truck } from 'lucide-react';
import { useEffect, useState } from 'react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

import { api } from '../api/client.js';

const colors = ['#2563eb', '#16a34a', '#f59e0b', '#dc2626', '#7c3aed', '#0891b2'];

function money(value) {
  return new Intl.NumberFormat('ru-RU', { maximumFractionDigits: 0 }).format(value || 0);
}

export default function DashboardPage() {
  const [summary, setSummary] = useState(null);
  const [expenses, setExpenses] = useState([]);
  const [months, setMonths] = useState([]);

  useEffect(() => {
    Promise.all([
      api.get('/analytics/summary'),
      api.get('/analytics/expenses-by-type'),
      api.get('/analytics/costs-by-month'),
    ]).then(([summaryRes, expenseRes, monthRes]) => {
      setSummary(summaryRes.data);
      setExpenses(expenseRes.data);
      setMonths(monthRes.data);
    });
  }, []);

  const metrics = [
    { label: 'Автомобили', value: summary?.vehicles_count || 0, icon: Truck },
    { label: 'Рейсы', value: summary?.trips_count || 0, icon: Route },
    { label: 'Общие расходы', value: `${money(summary?.total_cost)} ₽`, icon: CircleDollarSign },
    { label: 'Средняя цена/км', value: `${summary?.average_cost_per_km || 0} ₽`, icon: Activity },
  ];

  return (
    <section className="page">
      <header className="page-header">
        <div>
          <h1>Dashboard</h1>
          <p>Оперативная картина транспортных расходов предприятия.</p>
        </div>
      </header>

      <div className="metric-grid">
        {metrics.map((metric) => {
          const Icon = metric.icon;
          return (
            <article className="metric" key={metric.label}>
              <Icon size={22} />
              <span>{metric.label}</span>
              <strong>{metric.value}</strong>
            </article>
          );
        })}
      </div>

      <div className="analytics-grid">
        <section className="panel">
          <h2>Расходы по типам</h2>
          <div className="chart-box">
            <ResponsiveContainer>
              <PieChart>
                <Pie data={expenses} dataKey="value" nameKey="name" outerRadius={110} label>
                  {expenses.map((entry, index) => (
                    <Cell key={entry.name} fill={colors[index % colors.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => `${money(value)} ₽`} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </section>

        <section className="panel">
          <h2>Динамика расходов</h2>
          <div className="chart-box">
            <ResponsiveContainer>
              <LineChart data={months}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip formatter={(value) => `${money(value)} ₽`} />
                <Line type="monotone" dataKey="total_cost" stroke="#2563eb" strokeWidth={3} dot />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </section>

        <section className="panel panel-wide">
          <h2>Сравнение категорий расходов</h2>
          <div className="chart-box short">
            <ResponsiveContainer>
              <BarChart data={expenses}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip formatter={(value) => `${money(value)} ₽`} />
                <Bar dataKey="value" fill="#16a34a" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </section>
      </div>
    </section>
  );
}

