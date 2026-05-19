import { useEffect, useState } from 'react';

import { api } from '../api/client.js';
import CrudPage from '../components/CrudPage.jsx';

const today = new Date().toISOString().slice(0, 10);

export default function FuelLogsPage() {
  const [vehicles, setVehicles] = useState([]);
  const [trips, setTrips] = useState([]);

  useEffect(() => {
    Promise.all([api.get('/vehicles'), api.get('/trips')]).then(([vehicleRes, tripRes]) => {
      setVehicles(vehicleRes.data);
      setTrips(tripRes.data);
    });
  }, []);

  const vehicleOptions = vehicles.map((item) => ({ value: item.id, label: `${item.plate_number} - ${item.brand}` }));
  const tripOptions = trips.map((trip) => ({ value: trip.id, label: `Рейс #${trip.id} от ${trip.trip_date}` }));
  const vehicleById = Object.fromEntries(vehicles.map((item) => [item.id, item]));

  return (
    <CrudPage
      title="Учет топлива"
      subtitle="Заправки, литры, цена и фактические топливные затраты."
      endpoint="/fuel-logs"
      searchPlaceholder="Журнал топлива"
      fields={[
        { name: 'vehicle_id', label: 'Автомобиль', type: 'select', valueType: 'number', options: vehicleOptions },
        { name: 'trip_id', label: 'Рейс', type: 'select', valueType: 'number', options: tripOptions, required: false },
        { name: 'log_date', label: 'Дата', type: 'date', defaultValue: today },
        { name: 'liters', label: 'Литры', type: 'number', step: '0.01', defaultValue: 0 },
        { name: 'price_per_liter', label: 'Цена за литр', type: 'number', step: '0.01', defaultValue: 0 },
        { name: 'odometer_km', label: 'Одометр', type: 'number', step: '0.1', required: false },
      ]}
      columns={[
        { key: 'log_date', label: 'Дата' },
        { key: 'vehicle_id', label: 'Автомобиль', render: (row) => vehicleById[row.vehicle_id]?.plate_number || row.vehicle_id },
        { key: 'trip_id', label: 'Рейс', render: (row) => (row.trip_id ? `#${row.trip_id}` : '-') },
        { key: 'liters', label: 'Литры' },
        { key: 'price_per_liter', label: 'Цена' },
        { key: 'total_cost', label: 'Сумма' },
      ]}
    />
  );
}

