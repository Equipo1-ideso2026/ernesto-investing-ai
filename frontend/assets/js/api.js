/**
 * Cliente API de Ernesto Investing AI.
 * Unico archivo que sabe como se llama la URL del backend y como se
 * adjunta el token de sesion. Si la URL de ngrok cambia, solo se
 * actualiza aqui (o desde la pantalla de Configuracion).
 */
const ErnestoAPI = (() => {
  const CLAVE_API_URL = "ernesto_api_url";
  const CLAVE_TOKEN = "ernesto_token";
  const CLAVE_USUARIO = "ernesto_usuario";

  function obtenerApiUrl() {
    return localStorage.getItem(CLAVE_API_URL) || "";
  }

  function guardarApiUrl(url) {
    localStorage.setItem(CLAVE_API_URL, url.trim().replace(/\/+$/, ""));
  }

  function obtenerToken() {
    return localStorage.getItem(CLAVE_TOKEN);
  }

  function obtenerUsuario() {
    const crudo = localStorage.getItem(CLAVE_USUARIO);
    return crudo ? JSON.parse(crudo) : null;
  }

  function guardarSesion(token, usuario) {
    localStorage.setItem(CLAVE_TOKEN, token);
    localStorage.setItem(CLAVE_USUARIO, JSON.stringify(usuario));
  }

  function actualizarUsuario(usuario) {
    localStorage.setItem(CLAVE_USUARIO, JSON.stringify(usuario));
  }

  function cerrarSesion() {
    localStorage.removeItem(CLAVE_TOKEN);
    localStorage.removeItem(CLAVE_USUARIO);
    window.location.href = "index.html";
  }

  function estaAutenticado() {
    return Boolean(obtenerToken());
  }

  /**
   * Llamada generica a la API. Adjunta el token si existe, agrega el
   * header que evita la pantalla de advertencia de ngrok, y lanza un
   * Error con mensaje legible si la respuesta no es exitosa.
   */
  async function solicitar(ruta, opciones = {}) {
    const base = obtenerApiUrl();
    if (!base) {
      const error = new Error("API_NO_CONFIGURADA");
      error.codigo = "API_NO_CONFIGURADA";
      throw error;
    }

    const headers = {
      "Content-Type": "application/json",
      "ngrok-skip-browser-warning": "true",
      ...(opciones.headers || {}),
    };

    const token = obtenerToken();
    if (token) headers["Authorization"] = `Bearer ${token}`;

    let respuesta;
    try {
      respuesta = await fetch(`${base}${ruta}`, { cache: "no-store", ...opciones, headers });
    } catch (errorOriginal) {
      if (errorOriginal.name === "AbortError") throw errorOriginal;
      const error = new Error("No se pudo conectar con la API. Verifica la URL en Configuracion.");
      error.codigo = "SIN_CONEXION";
      throw error;
    }

    if (respuesta.status === 401) {
      cerrarSesion();
      const error = new Error("Tu sesion expiro. Inicia sesion nuevamente.");
      error.codigo = "SESION_EXPIRADA";
      throw error;
    }

    if (!respuesta.ok) {
      const cuerpo = await respuesta.json().catch(() => ({}));
      const error = new Error(cuerpo.detail || `Error ${respuesta.status} al consultar la API`);
      error.codigo = "ERROR_API";
      error.status = respuesta.status;
      throw error;
    }

    return respuesta.json();
  }

  function get(ruta, opciones = {}) {
    return solicitar(ruta, { method: "GET", ...opciones });
  }

  function post(ruta, cuerpo) {
    return solicitar(ruta, { method: "POST", body: JSON.stringify(cuerpo) });
  }

  function put(ruta, cuerpo) {
    return solicitar(ruta, { method: "PUT", body: JSON.stringify(cuerpo) });
  }

  return {
    obtenerApiUrl, guardarApiUrl,
    obtenerToken, obtenerUsuario, guardarSesion, actualizarUsuario, cerrarSesion,
    estaAutenticado,
    get, post, put,
  };
})();
