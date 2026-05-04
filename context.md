# PowerLytix Frontend Context

Este repositorio es el frontend Vue 3/Vite de PowerLytix, un dashboard IoT de monitoreo eléctrico. El backend esperado es Django REST + MySQL; el frontend no usa MQTT y solo debe consumir HTTP con Axios.

## Stack y estructura
- Vue 3 + Composition API + Vite.
- Vue Router en `src/router/index.js`.
- Pinia stores en `src/stores/`.
- Axios services en `src/services/`.
- Mock/fallback data en `src/mocks/devices.js`.
- Estilos globales en `src/assets/styles.css`.
- Componentes clave:
  - `src/components/layout/MainLayout.vue`
  - `src/components/ui/PowerlytixLogo.vue`
  - `src/components/ui/StatusBadge.vue`
  - `src/components/devices/DeviceCard.vue`
  - `src/components/devices/DeviceDetailDrawer.vue`
  - `src/components/devices/DeviceIcon.vue`
  - `src/components/charts/PowerLineChart.vue`
  - `src/components/charts/DeviceBarChart.vue`

## Rutas actuales
- `/login`
- `/register`
- `/monitor`
- `/analytics`
- `/admin/devices`
- `/profile`

Las rutas privadas requieren token en Pinia/localStorage. Login/register usan mock token si la API no responde.

## API preparada
- `POST /api/auth/login/`
- `POST /api/auth/register/`
- `GET /api/devices/`
- `GET /api/devices/:id/`
- `POST /api/devices/`
- `DELETE /api/devices/:id/`
- `GET /api/analytics/history/`
- `GET /api/cfe/summary/`
- `GET /api/user/profile/`

Los services tienen fallback rápido a mock data para que la UI no se congele si Django no está activo.

## UI y UX actual
- Tema visual SaaS claro/oscuro, emerald como color principal.
- Sidebar fija con Monitor, Análisis, Administrar.
- Perfil ya no está como tab principal: se abre desde el chip de usuario inferior con popup.
- Popups de idioma/usuario cierran con click fuera y al cambiar de ruta.
- Hay transiciones entre rutas, popups, drawer y gráficas.
- El selector de idioma está en sidebar y auth; actualmente traduce la interfaz ES/EN usando `src/stores/ui.js`.
- El botón de tema debe mostrarse solo como icono sol/luna, sin texto.

## Logo
- El logo único vive en `src/components/ui/PowerlytixLogo.vue`.
- Debe verse como rayo amarillo dentro de círculo emerald.
- Texto esperado: `POWERLYTIX`, misma tipografía, `POWER` semibold/bold moderado y `LYTIX` ligero.
- Debe usarse el mismo componente en login, register, sidebar y hero de Current Total Usage.

## Monitor
- `MonitorView.vue` muestra consumo total y dispositivos.
- DeviceCard solo muestra nombre, ID, potencia activa, estado y última actualización.
- El detalle se abre con el botón de opciones del dispositivo.
- `DeviceDetailDrawer.vue` mantiene polling suave y cierra con animación.
- El drawer debe mostrar el ícono seleccionado del dispositivo usando `DeviceIcon.vue`, no un rayo fijo.

## Analytics
- Gráfica principal custom SVG/CSS en `PowerLineChart.vue`, no Chart.js.
- Muestra promedio del periodo seleccionado, no consumo total actual.
- Puede sobreponer series de dispositivos con tonos verdes.
- Tooltip aparece al hover con consumo por instante.
- Leyenda de dispositivos debe aparecer solo al hover de la gráfica, como listado lateral izquierdo para no chocar con el trazado.
- Los puntos de hover se renderizan como elementos HTML de tamaño fijo para que se mantengan circulares aunque el SVG escale.
- `DeviceBarChart.vue` debe usar la misma paleta/orden de colores que las series de `PowerLineChart.vue`.
- Estadísticas generales usan formato limpio con línea lateral de color, no cards de fondo coloreado.

## Administración
- `DeviceAdminView.vue` permite agregar/eliminar dispositivos.
- Borrado requiere confirmación modal.
- Alta de dispositivo incluye selector de ícono.
- Íconos disponibles en `DeviceIcon.vue` incluyen aire, computadora, refrigerador, lavadora, microondas, lámpara, TV, ventilador, calefactor, router, impresora, teléfono, tablet, bocina, consola, cafetera, cocina, foco, batería, cable, contacto y general.

## Preferencias de implementación
- Mantener separación visual/API/mock.
- No implementar backend.
- No usar MQTT.
- Usar `apply_patch` para ediciones manuales.
- Verificar con `npm.cmd run build`; en este entorno suele requerir escalación por `spawn EPERM`.
