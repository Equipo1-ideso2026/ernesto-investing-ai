/**
 * Inyecta el shell de navegacion (sidebar) en cada pagina protegida
 * y lo deja funcionando: resalta el enlace activo, muestra los datos
 * del usuario autenticado y conecta el boton de cerrar sesion.
 *
 * Requiere que la pagina tenga un <div id="sidebar-contenedor"></div>
 * y haber cargado api.js antes que este script.
 */
async function inicializarShell() {
  requireAuth();

  const contenedor = document.getElementById("sidebar-contenedor");
  if (!contenedor) return;

  const html = await fetch("partials/sidebar.html").then((r) => r.text());
  contenedor.innerHTML = html;

  resaltarPaginaActiva();
  mostrarDatosUsuario();
  conectarBotonSalir();
  conectarMenuMovil();

  if (window.lucide) window.lucide.createIcons();
}

function resaltarPaginaActiva() {
  const pagina = document.body.dataset.pagina;
  if (!pagina) return;
  const enlace = document.querySelector(`.sidebar-link[data-nav="${pagina}"]`);
  enlace?.classList.add("activo");
}

function mostrarDatosUsuario() {
  const usuario = ErnestoAPI.obtenerUsuario();
  if (!usuario) return;

  const inicial = usuario.nombre_completo?.charAt(0).toUpperCase() || "?";
  const avatar = document.getElementById("avatar-usuario");
  const nombre = document.getElementById("nombre-usuario");
  const username = document.getElementById("username-usuario");

  if (avatar) avatar.textContent = inicial;
  if (nombre) nombre.textContent = usuario.nombre_completo;
  if (username) username.textContent = `@${usuario.username}`;
}

function conectarBotonSalir() {
  document.getElementById("boton-cerrar-sesion")?.addEventListener("click", () => {
    ErnestoAPI.cerrarSesion();
  });
}

function conectarMenuMovil() {
  const boton = document.getElementById("boton-menu-movil");
  const sidebar = document.getElementById("sidebar");
  boton?.addEventListener("click", () => sidebar?.classList.toggle("abierto"));
}

document.addEventListener("DOMContentLoaded", inicializarShell);
