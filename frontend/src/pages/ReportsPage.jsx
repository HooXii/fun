import { Download, RefreshCcw } from 'lucide-react';
import { useEffect, useState } from 'react';

import { api } from '../api/client.js';

function toCsv(rows) {
  if (!rows.length) {
    return '';
  }
  const headers = Object.keys(rows[0]);
  const escape = (value) => `"${String(value ?? '').replaceAll('"', '""')}"`;
  return [headers.join(';'), ...rows.map((row) => headers.map((header) => escape(row[header])).join(';'))].join('\n');
}

function saveCsv(name, rows) {
  const blob = new Blob([toCsv(rows)], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = name;
  link.click();
  URL.revokeObjectURL(url);
}

export default function ReportsPage() {
  const [tripRows, setTripRows] = useState([]);
  const [expenseRows, setExpenseRows] = useState([]);

  async function loadReports() {
    const [trips, expenses] = await Promise.all([api.get('/reports/trips'), api.get('/reports/expenses')]);
    setTripRows(trips.data);
    setExpenseRows(expenses.data);
  }

  useEffect(() => {
    loadReports();
  }, []);

  return (
    <section className="page">
      <header className="page-header">
        <div>
          <h1>Отчеты</h1>
          <p>Сводные таблицы по рейсам и расходам.</p>
        </div>
        <button className="secondary-button" type="button" onClick={loadReports}>
          <RefreshCcw size={17} />
          <span>Обновить</span>
        </button>
      </header>

      <section className="panel">
        <div className="section-title-row">
          <h2>Отчет по рейсам</h2>
          <button className="secondary-button" type="button" onClick={() => saveCsv('trips-report.csv', tripRows)}>
            <Download size={17} />
            <span>CSV</span>
          </button>
        </div>
        <div className="table-wrap plain">
          <table>
            <thead>
              <tr>
                <th>Рейс</th>
                <th>Дата</th>
                <th>Автомобиль</th>
                <th>Водитель</th>
                <th>Маршрут</th>
                <th>Себестоимость</th>
                <th>Цена/км</th>
                <th>Статус</th>
              </tr>
            </thead>
            <tbody>
              {tripRows.map((row) => (
                <tr key={row.trip_id}>
                  <td>#{row.trip_id}</td>
                  <td>{row.date}</td>
                  <td>{row.vehicle}</td>
                  <td>{row.driver}</td>
                  <td>{row.route}</td>
                  <td>{row.total_cost}</td>
                  <td>{row.cost_per_km}</td>
                  <td>{row.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="panel">
        <div className="section-title-row">
          <h2>Отчет по расходам</h2>
          <button className="secondary-button" type="button" onClick={() => saveCsv('expenses-report.csv', expenseRows)}>
            <Download size={17} />
            <span>CSV</span>
          </button>
        </div>
        <div className="table-wrap plain">
          <table>
            <thead>
              <tr>
                <th>Расход</th>
                <th>Рейс</th>
                <th>Маршрут</th>
                <th>Тип</th>
                <th>Сумма</th>
                <th>Описание</th>
              </tr>
            </thead>
            <tbody>
              {expenseRows.map((row) => (
                <tr key={row.expense_id}>
                  <td>#{row.expense_id}</td>
                  <td>#{row.trip_id}</td>
                  <td>{row.route}</td>
                  <td>{row.type}</td>
                  <td>{row.amount}</td>
                  <td>{row.description}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </section>
  );
}

