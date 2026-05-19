import CrudPage from '../components/CrudPage.jsx';

export default function VehiclesPage() {
  return (
    <CrudPage
      title="Учет автомобилей"
      subtitle="Автопарк предприятия и нормативный расход топлива."
      endpoint="/vehicles"
      searchPlaceholder="Госномер, марка или модель"
      fields={[
        { name: 'plate_number', label: 'Госномер' },
        { name: 'brand', label: 'Марка' },
        { name: 'model', label: 'Модель' },
        { name: 'year', label: 'Год', type: 'number', required: false },
        { name: 'fuel_type', label: 'Топливо', defaultValue: 'diesel' },
        { name: 'fuel_consumption_norm', label: 'Норма л/100 км', type: 'number', step: '0.1', defaultValue: 0 },
        { name: 'mileage', label: 'Пробег, км', type: 'number', step: '0.1', defaultValue: 0 },
        {
          name: 'status',
          label: 'Статус',
          type: 'select',
          defaultValue: 'active',
          options: [
            { value: 'active', label: 'Активен' },
            { value: 'repair', label: 'Ремонт' },
            { value: 'archived', label: 'Архив' },
          ],
        },
      ]}
      columns={[
        { key: 'plate_number', label: 'Госномер' },
        { key: 'brand', label: 'Марка' },
        { key: 'model', label: 'Модель' },
        { key: 'fuel_consumption_norm', label: 'Норма' },
        { key: 'mileage', label: 'Пробег' },
        { key: 'status', label: 'Статус' },
      ]}
    />
  );
}

