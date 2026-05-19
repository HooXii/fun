import CrudPage from '../components/CrudPage.jsx';

export default function DriversPage() {
  return (
    <CrudPage
      title="Учет водителей"
      subtitle="Водители, лицензии и базовая оплата за рейс."
      endpoint="/drivers"
      searchPlaceholder="ФИО или номер удостоверения"
      fields={[
        { name: 'full_name', label: 'ФИО' },
        { name: 'license_number', label: 'Водительское удостоверение' },
        { name: 'phone', label: 'Телефон', required: false },
        { name: 'salary_per_trip', label: 'Оплата за рейс', type: 'number', step: '0.01', defaultValue: 0 },
        {
          name: 'status',
          label: 'Статус',
          type: 'select',
          defaultValue: 'active',
          options: [
            { value: 'active', label: 'Активен' },
            { value: 'vacation', label: 'Отпуск' },
            { value: 'inactive', label: 'Неактивен' },
          ],
        },
      ]}
      columns={[
        { key: 'full_name', label: 'ФИО' },
        { key: 'license_number', label: 'Удостоверение' },
        { key: 'phone', label: 'Телефон' },
        { key: 'salary_per_trip', label: 'Оплата' },
        { key: 'status', label: 'Статус' },
      ]}
    />
  );
}

