// api_utils.js

// 🔧 Configuración base de la API (Sin espacios ni saltos de línea al final)
const API_BASE_URL = "http://127.0.0.1:8000";

// Claves de almacenamiento local
const K_AUTH = "rostiseria_auth";
const K_CART = "rostiseria_cart";

// ===================== AUTENTICACIÓN ===================== //

// Guarda token + email + flag admin
function saveAuth(token, email, isAdmin = false) {
    const data = { token, email, isAdmin };
    localStorage.setItem(K_AUTH, JSON.stringify(data));
}

// Recupera la sesión actual
function getAuth() {
    const raw = localStorage.getItem(K_AUTH);
    if (!raw) return null;
    try {
        return JSON.parse(raw);
    } catch {
        return null;
    }
}

// Devuelve email e isAdmin listos para usar
function getLoggedUser() {
    const auth = getAuth();
    if (!auth) return null;
    return {
        email: auth.email,
        isAdmin: !!auth.isAdmin,
    };
}

// Limpia sesión
function clearAuth() {
    localStorage.removeItem(K_AUTH);
}

// ===================== FETCH AUXILIAR ===================== //

async function apiFetch(path, method = "GET", body = null, requireAuth = false) {
    // Aseguramos que la URL esté limpia
    const url = API_BASE_URL + path;
    
    const headers = { "Content-Type": "application/json" };

    if (requireAuth) {
        const auth = getAuth();
        if (!auth || !auth.token) {
            throw new Error("No hay sesión activa");
        }
        headers["Authorization"] = `Bearer ${auth.token}`;
    }

    try {
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
            } catch (_) { }
            throw new Error(msg);
        }

        if (res.status === 204) return null;
        return await res.json();
    } catch (error) {
        throw error;
    }
}

// ===================== CARRITO ===================== //

function getCart() {
    const raw = localStorage.getItem(K_CART);
    if (!raw) return [];
    try { return JSON.parse(raw); } catch { return []; }
}

function saveCart(cart) {
    localStorage.setItem(K_CART, JSON.stringify(cart));
}

function clearCart() {
    localStorage.removeItem(K_CART);
}

function addToCart(producto) {
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

function showToast(message, type = "success") {
    const container = document.getElementById("toastContainer");
    if (!container) {
        alert(message);
        return;
    }
    // Usamos clases de Bootstrap para colores: success (verde), danger (rojo), warning (amarillo)
    const alertClass = type === 'error' ? 'danger' : type === 'listo' ? 'success' : type;
    
    const toast = document.createElement("div");
    toast.className = `alert alert-${alertClass} alert-dismissible fade show`;
    toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    container.appendChild(toast);
    // Auto-eliminar a los 4 segundos
    setTimeout(() => {
        try { toast.remove(); } catch(e){}
    }, 4000);
}

// Exponer funciones globalmente
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