import { Play, RefreshCcw, Settings2 } from 'lucide-react';
import { useEffect, useState } from 'react';

import { api } from '../api/client.js';

function money(value) {
  return new Intl.NumberFormat('ru-RU', { maximumFractionDigits: 2 }).format(value || 0);
}

export default function OptimizationPage() {
  const [runData, setRunData] = useState(null);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function loadResults() {
    const { data } = await api.get('/optimization/results');
    setResults(data);
  }

  useEffect(() => {
    loadResults();
  }, []);

  async function runOptimization() {
    setLoading(true);
    setError('');
    try {
      const { data } = await api.post('/optimization/run');
      setRunData(data);
      await loadResults();
    } catch (err) {
      setError(err.response?.data?.detail || 'Не удалось выполнить оптимизацию');
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="page">
      <header className="page-header">
        <div>
          <h1>Оптимизация расходов</h1>
          <p>Расчет себестоимости, цены километра, эффективности и рекомендаций.</p>
        </div>
        <div className="button-row">
          <button className="secondary-button" type="button" onClick={loadResults}>
            <RefreshCcw size={17} />
            <span>Обновить</span>
          </button>
          <button className="primary-button" type="button" onClick={runOptimization} disabled={loading}>
            <Play size={17} />
            <span>{loading ? 'Расчет...' : 'Запустить'}</span>
          </button>
        </div>
      </header>

      {error && <div className="alert">{error}</div>}

      <div className="optimization-band">
        <article className="metric">
          <Settings2 size={22} />
          <span>Обработано рейсов</span>
          <strong>{runData?.processed_trips ?? results.length}</strong>
        </article>
        <article className="metric">
          <Settings2 size={22} />
          <span>Самый дешевый маршрут</span>
          <strong>{runData?.cheapest_route?.name || 'Нет данных'}</strong>
        </article>
        <article className="metric">
          <Settings2 size={22} />
          <span>Самый дорогой рейс</span>
          <strong>{runData?.most_expensive_trip ? `#${runData.most_expensive_trip.trip_id}` : 'Нет данных'}</strong>
        </article>
      </div>

      {runData?.high_fuel_vehicles?.length > 0 && (
        <section className="panel">
          <h2>Автомобили с высоким расходом топлива</h2>
          <div className="table-wrap plain">
            <table>
              <thead>
                <tr>
                  <th>Автомобиль</th>
                  <th>Норма</th>
                  <th>Факт</th>
                  <th>Превышение</th>
                </tr>
              </thead>
              <tbody>
                {runData.high_fuel_vehicles.map((vehicle) => (
                  <tr key={vehicle.vehicle_id}>
                    <td>{vehicle.plate_number}</td>
                    <td>{vehicle.norm_l_per_100km} л/100 км</td>
                    <td>{vehicle.actual_l_per_100km} л/100 км</td>
                    <td>{vehicle.overrun_percent}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      <section className="panel">
        <h2>Результаты оптимизации</h2>
        <div className="table-wrap plain">
          <table>
            <thead>
              <tr>
                <th>Рейс</th>
                <th>Себестоимость</th>
                <th>Цена/км</th>
                <th>Эффективность</th>
                <th>Рекомендация</th>
              </tr>
            </thead>
            <tbody>
              {results.length === 0 ? (
                <tr>
                  <td colSpan="5">Запустите оптимизацию для формирования рекомендаций</td>
                </tr>
              ) : (
                results.map((item) => (
                  <tr key={item.id}>
                    <td>#{item.trip_id}</td>
                    <td>{money(item.total_cost)} ₽</td>
                    <td>{money(item.cost_per_km)} ₽</td>
                    <td>{item.efficiency_score}</td>
                    <td>{item.recommendation}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </section>
    </section>
  );
}

