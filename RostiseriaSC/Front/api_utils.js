// api_utils.js

// 🔧 Configuración base de la API
const API_BASE_URL = "http://127.0.0.1:8000";

// Claves de almacenamiento local
const K_AUTH = "rostiseria_auth";
const K_CART = "rostiseria_cart";

// ===================== AUTENTICACIÓN ===================== //

// Guarda token + email + flag admin
export function saveAuth(token, email, isAdmin = false) {
    const data = { token, email, isAdmin };
    localStorage.setItem(K_AUTH, JSON.stringify(data));
}

// Recupera la sesión actual
export function getAuth() {
    const raw = localStorage.getItem(K_AUTH);
    if (!raw) return null;
    try {
        return JSON.parse(raw);
    } catch {
        return null;
    }
}

// Devuelve email e isAdmin listos para usar
export function getLoggedUser() {
    const auth = getAuth();
    if (!auth) return null;
    return {
        email: auth.email,
        isAdmin: !!auth.isAdmin,
    };
}

// Limpia sesión
export function clearAuth() {
    localStorage.removeItem(K_AUTH);
}

// ===================== FETCH AUXILIAR ===================== //

// 🔗 Helper general para llamar a la API con JSON y (opcional) token
export async function apiFetch(path, method = "GET", body = null, requireAuth = false) {
    const url = API_BASE_URL + path;
    const headers = { "Content-Type": "application/json" };

    if (requireAuth) {
        const auth = getAuth();
        if (!auth || !auth.token) {
            throw new Error("No hay sesión activa");
        }
        headers["Authorization"] = `Bearer ${auth.token}`;
    }

    const res = await fetch(url, {
        method,
        headers,
        body: body ? JSON.stringify(body) : null,
    });

    if (!res.ok) {
        let msg = `Error HTTP ${res.status}`;
        try {
            const data = await res.json();
            if (data && data.detail) {
                msg = Array.isArray(data.detail)
                    ? data.detail.map(d => d.msg || d).join(", ")
                    : data.detail;
            }
        } catch (_) {
            // ignorar
        }
        throw new Error(msg);
    }

    // 204 sin cuerpo
    if (res.status === 204) return null;

    return await res.json();
}

// ===================== CARRITO ===================== //

// Obtiene carrito desde localStorage
export function getCart() {
    const raw = localStorage.getItem(K_CART);
    if (!raw) return [];
    try {
        return JSON.parse(raw);
    } catch {
        return [];
    }
}

// Guarda carrito en localStorage
export function saveCart(cart) {
    localStorage.setItem(K_CART, JSON.stringify(cart));
}

// Limpia carrito
export function clearCart() {
    localStorage.removeItem(K_CART);
}

// Agrega un producto al carrito (o aumenta cantidad)
export function addToCart(producto) {
    const cart = getCart();
    const idx = cart.findIndex(p => p.id === producto.id);
    if (idx >= 0) {
        cart[idx].cantidad += producto.cantidad || 1;
    } else {
        cart.push({ ...producto, cantidad: producto.cantidad || 1 });
    }
    saveCart(cart);
}

// ===================== UTILIDADES UI ===================== //

// Muestra un toast simple Bootstrap-like (si existe container) o alert fallback
export function showToast(message, type = "success") {
    const container = document.getElementById("toastContainer");
    if (!container) {
        alert(message);
        return;
    }

    const toast = document.createElement("div");
    toast.className = `alert alert-${type}`;
    toast.textContent = message;

    container.appendChild(toast);
    setTimeout(() => toast.remove(), 4000);
}

// Expone algunas funciones en window (para uso en <script> inline)
window.API_BASE_URL = API_BASE_URL;
window.saveAuth = saveAuth;
window.getAuth = getAuth;
window.getLoggedUser = getLoggedUser;
window.clearAuth = clearAuth;
window.apiFetch = apiFetch;
window.getCart = getCart;
window.saveCart = saveCart;
window.clearCart = clearCart;
window.addToCart = addToCart;
window.showToast = showToast;
