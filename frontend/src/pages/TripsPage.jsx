import { useEffect, useState } from 'react';

import { api } from '../api/client.js';
import CrudPage from '../components/CrudPage.jsx';

const today = new Date().toISOString().slice(0, 10);

export default function TripsPage() {
  const [vehicles, setVehicles] = useState([]);
  const [drivers, setDrivers] = useState([]);
  const [routes, setRoutes] = useState([]);

  useEffect(() => {
    Promise.all([api.get('/vehicles'), api.get('/drivers'), api.get('/routes')]).then(([vehicleRes, driverRes, routeRes]) => {
      setVehicles(vehicleRes.data);
      setDrivers(driverRes.data);
      setRoutes(routeRes.data);
    });
  }, []);

  const vehicleOptions = vehicles.map((item) => ({ value: item.id, label: `${item.plate_number} - ${item.brand} ${item.model}` }));
  const driverOptions = drivers.map((item) => ({ value: item.id, label: item.full_name }));
  const routeOptions = routes.map((item) => ({ value: item.id, label: `${item.name} (${item.distance_km} км)` }));
  const vehicleById = Object.fromEntries(vehicles.map((item) => [item.id, item]));
  const driverById = Object.fromEntries(drivers.map((item) => [item.id, item]));
  const routeById = Object.fromEntries(routes.map((item) => [item.id, item]));

  return (
    <CrudPage
      title="Учет рейсов"
      subtitle="Центральный журнал рейсов с автоматическим расчетом себестоимости."
      endpoint="/trips"
      searchPlaceholder="Фильтр не обязателен"
      fields={[
        { name: 'vehicle_id', label: 'Автомобиль', type: 'select', valueType: 'number', options: vehicleOptions },
        { name: 'driver_id', label: 'Водитель', type: 'select', valueType: 'number', options: driverOptions },
        { name: 'route_id', label: 'Маршрут', type: 'select', valueType: 'number', options: routeOptions },
        { name: 'trip_date', label: 'Дата', type: 'date', defaultValue: today },
        { name: 'cargo_weight_tons', label: 'Груз, т', type: 'number', step: '0.1', defaultValue: 0 },
        { name: 'empty_mileage_km', label: 'Холостой пробег, км', type: 'number', step: '0.1', defaultValue: 0 },
        { name: 'driver_salary', label: 'Оплата водителя', type: 'number', step: '0.01', defaultValue: 0 },
        { name: 'fuel_cost', label: 'Топливо вручную', type: 'number', step: '0.01', defaultValue: 0 },
        { name: 'maintenance_cost', label: 'ТО вручную', type: 'number', step: '0.01', defaultValue: 0 },
        { name: 'tolls', label: 'Платные дороги', type: 'number', step: '0.01', defaultValue: 0 },
        { name: 'depreciation', label: 'Амортизация', type: 'number', step: '0.01', defaultValue: 0 },
        { name: 'other_costs', label: 'Прочее', type: 'number', step: '0.01', defaultValue: 0 },
        {
          name: 'status',
          label: 'Статус',
          type: 'select',
          defaultValue: 'planned',
          options: [
            { value: 'planned', label: 'План' },
            { value: 'in_progress', label: 'В пути' },
            { value: 'completed', label: 'Завершен' },
            { value: 'cancelled', label: 'Отменен' },
          ],
        },
        { name: 'notes', label: 'Комментарий', type: 'textarea', required: false },
      ]}
      columns={[
        { key: 'trip_date', label: 'Дата' },
        { key: 'vehicle_id', label: 'Автомобиль', render: (row) => vehicleById[row.vehicle_id]?.plate_number || row.vehicle_id },
        { key: 'driver_id', label: 'Водитель', render: (row) => driverById[row.driver_id]?.full_name || row.driver_id },
        { key: 'route_id', label: 'Маршрут', render: (row) => routeById[row.route_id]?.name || row.route_id },
        { key: 'total_cost', label: 'Себестоимость' },
        { key: 'cost_per_km', label: 'Цена/км' },
        { key: 'efficiency_score', label: 'Эффективность' },
        { key: 'status', label: 'Статус' },
      ]}
    />
  );
}

