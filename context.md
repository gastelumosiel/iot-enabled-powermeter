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
- `/cfe`
- `/admin/devices`
- `/profile`

Las rutas privadas requieren token en Pinia/localStorage. Login/register usan mock token si la API no responde.

## API preparada
- `POST /api/auth/login/`
- `POST /api/auth/register/`
- `GET /api/devices/`
- `GET /api/devices/:id/`
- `POST /api/devices/`
- `PATCH /api/devices/:id/`
- `DELETE /api/devices/:id/`
- `GET /api/analytics/history/`
- `GET /api/cfe/summary/`
- `GET /api/user/profile/`

Los services tienen fallback rápido a mock data para que la UI no se congele si Django no está activo.

## UI y UX actual
- Tema visual SaaS claro/oscuro, emerald como color principal.
- Sidebar fija con Monitor, Análisis, CFE y Administrar.
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
- El drawer muestra encabezados con íconos semánticos para Parámetros de Potencia, Parámetros Eléctricos e Información Adicional. Las barras laterales de cada métrica usan colores únicos entre potencias y parámetros eléctricos.

## Analytics
- Gráfica principal custom SVG/CSS en `PowerLineChart.vue`, no Chart.js.
- Muestra promedio del periodo seleccionado, no consumo total actual.
- Al cambiar parámetro/unidad, la gráfica debe repetir la transición `chart-soft` como cuando carga por primera vez.
- Puede sobreponer series de dispositivos con tonos verdes.
- Permite seleccionar dispositivos individualmente o usar "Seleccionar todos".
- Permite cambiar rango temporal entre 1h, 8h, 24h, 7d, 30d, 3m, 6m y 12m.
- Permite cambiar el parametro graficado: potencia activa/reactiva/aparente, voltaje, corriente, PF, frecuencia y fase.
- El dropdown de parametro en Analytics debe mostrar unidades, por ejemplo `Potencia Activa (W)` o `Fase (°)`.
- La vista refresca lecturas con polling suave y regenera las series con los valores actuales mock/API.
- Las barras inferiores representan el promedio por dispositivo del periodo y parametro seleccionados, no la lectura instantanea.
- El valor principal de Analytics debe sumar los promedios por dispositivo seleccionado; no debe promediar los promedios cuando hay varios dispositivos.
- Analytics ya no debe mostrar "Estadisticas generales"; `Consumo por dispositivo` ocupa el ancho completo inferior.
- Tooltip aparece al hover con consumo por instante.
- Leyenda de dispositivos debe aparecer solo al hover de la gráfica, como listado lateral izquierdo para no chocar con el trazado.
- Los puntos de hover se renderizan como elementos HTML de tamaño fijo para que se mantengan circulares aunque el SVG escale.
- `DeviceBarChart.vue` debe usar la misma paleta/orden de colores que las series de `PowerLineChart.vue`; la paleta ya no debe ser solamente verde para que los dispositivos sean distinguibles.
- Estadísticas generales usan formato limpio con línea lateral de color, no cards de fondo coloreado.

## Administración
- `DeviceAdminView.vue` permite agregar/eliminar dispositivos.
- Permite editar el nombre del dispositivo inline con botón de lápiz y `PATCH /api/devices/:id/`.
- La edición inline también permite cambiar el icono del dispositivo.
- Borrado requiere confirmación modal.
- Alta de dispositivo incluye selector de ícono.
- Íconos disponibles en `DeviceIcon.vue` incluyen aire, computadora, refrigerador, lavadora, microondas, lámpara, TV, ventilador, calefactor, router, impresora, teléfono, tablet, bocina, consola, cafetera, cocina, foco, batería, cable, contacto y general.

## CFE
- `CfeView.vue` vive en `/cfe`.
- La tarifa CFE ya no aparece dentro de estadísticas generales de Analytics.
- Permite escoger tarifa simulada, ajustar límite bimestral y guardar preferencias en localStorage.
- Muestra costo estimado total, progreso de uso respecto al límite y costo por dispositivo usando `energy_kwh`.
- Nota actualizada: ahora permite escoger tarifa doméstica CFE y fecha de inicio del periodo del recibo; calcula bimestres móviles.
- Nota actualizada: el límite bimestral se deriva de la tarifa seleccionada, intenta consumir `/api/cfe/tariffs/`, y usa fallback por bloques básico/intermedio/excedente con enlaces oficiales de CFE.
- Nota actualizada: muestra margen de consumo actual además del costo estimado, progreso y costo por dispositivo.
- Nota actualizada: CFE usa semaforo mensual por bloque basico/intermedio/excedente con indicador de consumo actual y muestra el precio/kWh del bloque vigente.
- CFE y Analytics deben mostrar el icono configurado del dispositivo en listas de consumo/costo.
- La animacion en CFE aplica solo al medidor/costo estimado y al boton de fuente oficial cuando llega la tarifa; los recuadros base no deben retrasarse.
- Nota actual: el boton "Fuente oficial CFE" debe estar visible desde el inicio; la animacion solo aplica al semaforo dentro del medidor cuando aparece por primera vez.
- El cambio de idioma usa una microanimacion global sin remontar la vista ni perder estado.
- Nota actualizada: CFE no debe tener animacion interna adicional en el recuadro de costo; todo aparece con la transicion normal de ruta/pestana.
- `CfeView.vue` debe inicializar la tarifa con `cfeService.localTariff(...)` para que el recuadro de costo estimado aparezca desde el primer render, sin esperar API/fallback async.
- En CFE, costo estimado actual va arriba izquierda y configuracion de tarifa arriba derecha; costo por dispositivo ocupa todo el ancho inferior.
- En CFE, los campos de configuración son borrador: el desglose de tarifa, medidor, costos y periodo aplicado no cambian hasta presionar Guardar. Al guardar se muestra temporalmente `Guardado con éxito` junto al botón y se emite `powerlytix:cfe-settings-saved`.
- `ProfileView.vue` debe reflejar la tarifa CFE guardada en localStorage (`powerlytix_cfe_rate`) y recalcular el límite bimestral como `monthlyLimit * 2`.
- En Analytics, el historial de consumo debe caber visualmente al entrar a la pestaña sin que la grafica quede cortada inicialmente; usar card/grafica compacta.
- En dark mode, la grafica custom debe tener fondo transparente y sin borde/sombra clara interna.
- La leyenda y tooltip de `PowerLineChart.vue` deben soportar hasta 20 dispositivos con scroll interno para no perder los ultimos elementos.
- Importante: la leyenda y tooltip deben tener `pointer-events: auto`; si se usa `pointer-events: none`, el scroll interno no funciona.
- Nota actual: en `PowerLineChart.vue` ya no hay leyenda fija de dispositivos dentro de la grafica; el tooltip de hover es la fuente de detalle. La grafica reserva un carril izquierdo para el tooltip, que aparece con animacion, tiene scroll interno oscuro en dark mode y trunca nombres largos despues de 15 caracteres para mantener visible el valor medido. El `key` de la transicion no incluye valores de lectura para que el polling no reinicie la animacion. El hover corrige el offset considerando el padding interno del viewBox. Cada serie renderiza un area clara completa desde su linea hasta la base de la grafica, sin gradiente, y esa area empieza/termina exactamente con la traza para que no haya color fuera del tramo real.
- El cambio de idioma y tema usa `ui-shift`, una microanimacion sin movimiento para evitar temblor.
- El medidor/costo estimado de CFE debe repetir `chart-soft` al cambiar tarifa, periodo o consumo relevante.
- El semaforo CFE debe mantener cortes limpios entre verde/amarillo/rojo.

## Preferencias de implementación
- Mantener separación visual/API/mock.
- No implementar backend.
- No usar MQTT.
- Usar `apply_patch` para ediciones manuales.
- Verificar con `npm.cmd run build`; en este entorno suele requerir escalación por `spawn EPERM`.
- El favicon actual es `public/powerlytix-favicon.svg` y debe reemplazar el icono de Vue/Vite.
