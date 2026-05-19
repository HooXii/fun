import CrudPage from '../components/CrudPage.jsx';

export default function RoutesPage() {
  return (
    <CrudPage
      title="Учет маршрутов"
      subtitle="Маршруты, расстояния, плановое время и платные участки."
      endpoint="/routes"
      searchPlaceholder="Название, пункт отправления или назначения"
      fields={[
        { name: 'name', label: 'Название' },
        { name: 'origin', label: 'Откуда' },
        { name: 'destination', label: 'Куда' },
        { name: 'distance_km', label: 'Расстояние, км', type: 'number', step: '0.1' },
        { name: 'planned_duration_hours', label: 'План, часов', type: 'number', step: '0.1', defaultValue: 0 },
        { name: 'tolls_estimate', label: 'Платные дороги', type: 'number', step: '0.01', defaultValue: 0 },
      ]}
      columns={[
        { key: 'name', label: 'Маршрут' },
        { key: 'origin', label: 'Откуда' },
        { key: 'destination', label: 'Куда' },
        { key: 'distance_km', label: 'Км' },
        { key: 'planned_duration_hours', label: 'Часы' },
        { key: 'tolls_estimate', label: 'Платные дороги' },
      ]}
    />
  );
}

