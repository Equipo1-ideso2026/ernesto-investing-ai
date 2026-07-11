/**
 * Autenticacion de Ernesto Investing AI.
 * Maneja los formularios de login/registro en index.html y expone
 * requireAuth() para que cada pagina protegida redirija al login
 * si no hay sesion activa.
 */

/** Llamar al inicio de cualquier pagina que requiera sesion activa. */
function requireAuth() {
  if (!ErnestoAPI.estaAutenticado()) {
    window.location.href = "index.html";
  }
}

function mostrarError(elemento, mensaje) {
  elemento.textContent = mensaje;
  elemento.style.display = "block";
}

function ocultarError(elemento) {
  elemento.style.display = "none";
}

document.addEventListener("DOMContentLoaded", () => {
  // Si ya hay sesion activa y estamos en el login, ir directo al dashboard
  if (document.body.dataset.pagina === "login" && ErnestoAPI.estaAutenticado()) {
    window.location.href = "dashboard.html";
    return;
  }

  inicializarConfiguracionApi();
  inicializarFormularioLogin();
  inicializarFormularioRegistro();
  inicializarAlternanciaFormularios();
});

function inicializarConfiguracionApi() {
  const input = document.getElementById("input-api-url");
  const boton = document.getElementById("boton-guardar-api-url");
  if (!input || !boton) return;

  input.value = ErnestoAPI.obtenerApiUrl();

  boton.addEventListener("click", () => {
    if (!input.value.trim()) return;
    ErnestoAPI.guardarApiUrl(input.value);
    boton.textContent = "Guardado";
    setTimeout(() => (boton.textContent = "Guardar URL"), 1500);
  });
}

function inicializarFormularioLogin() {
  const formulario = document.getElementById("formulario-login");
  if (!formulario) return;

  const errorBox = document.getElementById("error-login");

  formulario.addEventListener("submit", async (evento) => {
    evento.preventDefault();
    ocultarError(errorBox);

    const boton = formulario.querySelector("button[type=submit]");
    const textoOriginal = boton.textContent;
    boton.textContent = "Ingresando...";
    boton.disabled = true;

    try {
      const datos = {
        username: formulario.username.value.trim(),
        password: formulario.password.value,
      };
      const respuesta = await ErnestoAPI.post("/api/auth/login", datos);
      ErnestoAPI.guardarSesion(respuesta.token, respuesta.usuario);
      window.location.href = "dashboard.html";
    } catch (error) {
      mostrarError(errorBox, traducirErrorAuth(error));
    } finally {
      boton.textContent = textoOriginal;
      boton.disabled = false;
    }
  });
}

function inicializarFormularioRegistro() {
  const formulario = document.getElementById("formulario-registro");
  if (!formulario) return;

  const errorBox = document.getElementById("error-registro");

  formulario.addEventListener("submit", async (evento) => {
    evento.preventDefault();
    ocultarError(errorBox);

    if (formulario.password.value !== formulario.confirmar_password.value) {
      mostrarError(errorBox, "Las contrasenas no coinciden");
      return;
    }

    const boton = formulario.querySelector("button[type=submit]");
    const textoOriginal = boton.textContent;
    boton.textContent = "Creando cuenta...";
    boton.disabled = true;

    try {
      const datos = {
        nombre_completo: formulario.nombre_completo.value.trim(),
        email: formulario.email.value.trim(),
        username: formulario.username.value.trim(),
        password: formulario.password.value,
      };
      const respuesta = await ErnestoAPI.post("/api/auth/registro", datos);
      ErnestoAPI.guardarSesion(respuesta.token, respuesta.usuario);
      window.location.href = "dashboard.html";
    } catch (error) {
      mostrarError(errorBox, traducirErrorAuth(error));
    } finally {
      boton.textContent = textoOriginal;
      boton.disabled = false;
    }
  });
}

function inicializarAlternanciaFormularios() {
  const panelLogin = document.getElementById("panel-login");
  const panelRegistro = document.getElementById("panel-registro");
  const irARegistro = document.getElementById("ir-a-registro");
  const irALogin = document.getElementById("ir-a-login");

  if (!panelLogin || !panelRegistro) return;

  irARegistro?.addEventListener("click", (e) => {
    e.preventDefault();
    panelLogin.style.display = "none";
    panelRegistro.style.display = "block";
  });

  irALogin?.addEventListener("click", (e) => {
    e.preventDefault();
    panelRegistro.style.display = "none";
    panelLogin.style.display = "block";
  });
}

function traducirErrorAuth(error) {
  if (error.codigo === "API_NO_CONFIGURADA") {
    return "Primero configura la URL de la API (seccion debajo del formulario).";
  }
  if (error.codigo === "SIN_CONEXION") {
    return "No se pudo conectar con el servidor. Verifica que la API este activa en Colab.";
  }
  return error.message || "Ocurrio un error inesperado.";
}
