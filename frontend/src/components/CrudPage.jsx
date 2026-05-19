import { Edit3, RefreshCcw, Save, Search, Trash2, X } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';

import { api } from '../api/client.js';

function normalizeValue(field, value) {
  if (value === '' || value === undefined) {
    return field.required === false ? null : field.type === 'number' ? 0 : '';
  }
  if (field.type === 'number') {
    return Number(value);
  }
  if (field.valueType === 'number') {
    return Number(value);
  }
  return value;
}

function buildInitialForm(fields) {
  return fields.reduce((acc, field) => {
    acc[field.name] = field.defaultValue ?? '';
    return acc;
  }, {});
}

export default function CrudPage({ title, subtitle, endpoint, fields, columns, searchPlaceholder = 'Поиск' }) {
  const [rows, setRows] = useState([]);
  const [form, setForm] = useState(() => buildInitialForm(fields));
  const [editingId, setEditingId] = useState(null);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const initialForm = useMemo(() => buildInitialForm(fields), [fields]);

  async function loadRows(params = {}) {
    setLoading(true);
    setError('');
    try {
      const { data } = await api.get(endpoint, { params });
      setRows(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Не удалось загрузить данные');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadRows();
  }, [endpoint]);

  function handleChange(name, value) {
    setForm((current) => ({ ...current, [name]: value }));
  }

  function resetForm() {
    setForm(initialForm);
    setEditingId(null);
  }

  async function handleSubmit(event) {
    event.preventDefault();
    const payload = fields.reduce((acc, field) => {
      acc[field.name] = normalizeValue(field, form[field.name]);
      return acc;
    }, {});

    try {
      if (editingId) {
        await api.put(`${endpoint}/${editingId}`, payload);
      } else {
        await api.post(endpoint, payload);
      }
      resetForm();
      await loadRows(search ? { search } : {});
    } catch (err) {
      setError(err.response?.data?.detail || 'Не удалось сохранить запись');
    }
  }

  function startEdit(row) {
    const nextForm = fields.reduce((acc, field) => {
      const value = row[field.name];
      acc[field.name] = field.type === 'date' && value ? String(value).slice(0, 10) : value ?? '';
      return acc;
    }, {});
    setForm(nextForm);
    setEditingId(row.id);
  }

  async function removeRow(row) {
    if (!window.confirm('Удалить запись?')) {
      return;
    }
    try {
      await api.delete(`${endpoint}/${row.id}`);
      await loadRows(search ? { search } : {});
    } catch (err) {
      setError(err.response?.data?.detail || 'Не удалось удалить запись');
    }
  }

  async function handleSearch(event) {
    event.preventDefault();
    await loadRows(search ? { search } : {});
  }

  return (
    <section className="page">
      <header className="page-header">
        <div>
          <h1>{title}</h1>
          {subtitle && <p>{subtitle}</p>}
        </div>
        <button className="secondary-button" type="button" onClick={() => loadRows(search ? { search } : {})}>
          <RefreshCcw size={17} />
          <span>Обновить</span>
        </button>
      </header>

      <form className="toolbar" onSubmit={handleSearch}>
        <label className="search-field">
          <Search size={18} />
          <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder={searchPlaceholder} />
        </label>
        <button className="secondary-button" type="submit">
          <Search size={17} />
          <span>Найти</span>
        </button>
      </form>

      {error && <div className="alert">{error}</div>}

      <form className="form-panel" onSubmit={handleSubmit}>
        <div className="form-grid">
          {fields.map((field) => (
            <label key={field.name} className={field.type === 'textarea' ? 'field field-wide' : 'field'}>
              <span>{field.label}</span>
              {field.type === 'select' ? (
                <select
                  value={form[field.name] ?? ''}
                  onChange={(event) => handleChange(field.name, event.target.value)}
                  required={field.required !== false}
                >
                  <option value="">Выберите</option>
                  {(field.options || []).map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              ) : field.type === 'textarea' ? (
                <textarea value={form[field.name] ?? ''} onChange={(event) => handleChange(field.name, event.target.value)} />
              ) : (
                <input
                  type={field.type || 'text'}
                  step={field.step || undefined}
                  value={form[field.name] ?? ''}
                  onChange={(event) => handleChange(field.name, event.target.value)}
                  required={field.required !== false}
                />
              )}
            </label>
          ))}
        </div>
        <div className="form-actions">
          <button className="primary-button" type="submit">
            <Save size={17} />
            <span>{editingId ? 'Сохранить' : 'Добавить'}</span>
          </button>
          {editingId && (
            <button className="secondary-button" type="button" onClick={resetForm}>
              <X size={17} />
              <span>Отмена</span>
            </button>
          )}
        </div>
      </form>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              {columns.map((column) => (
                <th key={column.key}>{column.label}</th>
              ))}
              <th className="actions-col">Действия</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={columns.length + 1}>Загрузка данных...</td>
              </tr>
            ) : rows.length === 0 ? (
              <tr>
                <td colSpan={columns.length + 1}>Нет записей</td>
              </tr>
            ) : (
              rows.map((row) => (
                <tr key={row.id}>
                  {columns.map((column) => (
                    <td key={column.key}>{column.render ? column.render(row) : row[column.key]}</td>
                  ))}
                  <td className="row-actions">
                    <button className="icon-button" type="button" onClick={() => startEdit(row)} title="Редактировать">
                      <Edit3 size={16} />
                    </button>
                    <button className="icon-button danger" type="button" onClick={() => removeRow(row)} title="Удалить">
                      <Trash2 size={16} />
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}

