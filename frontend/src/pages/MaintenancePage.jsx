import { useEffect, useState } from 'react';

import { api } from '../api/client.js';
import CrudPage from '../components/CrudPage.jsx';

const today = new Date().toISOString().slice(0, 10);

export default function MaintenancePage() {
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
      title="Техническое обслуживание"
      subtitle="Затраты на обслуживание автомобилей и ремонт."
      endpoint="/maintenance"
      searchPlaceholder="Журнал обслуживания"
      fields={[
        { name: 'vehicle_id', label: 'Автомобиль', type: 'select', valueType: 'number', options: vehicleOptions },
        { name: 'trip_id', label: 'Рейс', type: 'select', valueType: 'number', options: tripOptions, required: false },
        { name: 'service_date', label: 'Дата', type: 'date', defaultValue: today },
        { name: 'maintenance_type', label: 'Тип обслуживания' },
        { name: 'cost', label: 'Стоимость', type: 'number', step: '0.01', defaultValue: 0 },
        { name: 'description', label: 'Описание', type: 'textarea', required: false },
      ]}
      columns={[
        { key: 'service_date', label: 'Дата' },
        { key: 'vehicle_id', label: 'Автомобиль', render: (row) => vehicleById[row.vehicle_id]?.plate_number || row.vehicle_id },
        { key: 'trip_id', label: 'Рейс', render: (row) => (row.trip_id ? `#${row.trip_id}` : '-') },
        { key: 'maintenance_type', label: 'Тип' },
        { key: 'cost', label: 'Стоимость' },
        { key: 'description', label: 'Описание' },
      ]}
    />
  );
}

