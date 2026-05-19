import { useEffect, useState } from 'react';

import { api } from '../api/client.js';
import CrudPage from '../components/CrudPage.jsx';

const expenseTypes = [
  { value: 'fuel', label: 'Топливо' },
  { value: 'driver_salary', label: 'Оплата водителя' },
  { value: 'maintenance', label: 'Обслуживание' },
  { value: 'tolls', label: 'Платные дороги' },
  { value: 'depreciation', label: 'Амортизация' },
  { value: 'other', label: 'Прочее' },
];

export default function ExpensesPage() {
  const [trips, setTrips] = useState([]);

  useEffect(() => {
    api.get('/trips').then((res) => setTrips(res.data));
  }, []);

  const tripOptions = trips.map((trip) => ({ value: trip.id, label: `Рейс #${trip.id} от ${trip.trip_date}` }));
  const tripById = Object.fromEntries(trips.map((trip) => [trip.id, trip]));

  return (
    <CrudPage
      title="Учет расходов"
      subtitle="Детализация затрат по каждому рейсу."
      endpoint="/expenses"
      searchPlaceholder="Поиск по журналу расходов"
      fields={[
        { name: 'trip_id', label: 'Рейс', type: 'select', valueType: 'number', options: tripOptions },
        { name: 'expense_type', label: 'Тип расхода', type: 'select', defaultValue: 'other', options: expenseTypes },
        { name: 'amount', label: 'Сумма', type: 'number', step: '0.01', defaultValue: 0 },
        { name: 'description', label: 'Описание', type: 'textarea', required: false },
      ]}
      columns={[
        { key: 'trip_id', label: 'Рейс', render: (row) => `#${row.trip_id} ${tripById[row.trip_id]?.trip_date || ''}` },
        { key: 'expense_type', label: 'Тип' },
        { key: 'amount', label: 'Сумма' },
        { key: 'description', label: 'Описание' },
      ]}
    />
  );
}

