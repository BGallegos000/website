const API_BASE_URL = 'http://localhost:8000'; 
const TOKEN_KEY = 'rostiseria_auth_token';
const USER_KEY = 'rostiseria_loggedUser';
const CART_KEY = 'rostiseria_cart';

// --- Auth ---
function saveAuth(token, email, isAdmin) {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(USER_KEY, JSON.stringify({ email, isAdmin }));
}
function getAuthToken() { return localStorage.getItem(TOKEN_KEY); }
function getLoggedUser() {
    try { return JSON.parse(localStorage.getItem(USER_KEY)); } catch { return null; }
}
function logout() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
}
function isAdmin() {
    const u = getLoggedUser();
    return u && u.isAdmin;
}

// --- Fetch Wrapper ---
async function apiFetch(endpoint, method = 'GET', body = null, requiresAuth = false) {
    const url = `${API_BASE_URL}${endpoint}`;
    const headers = { 'Content-Type': 'application/json' };
    
    if (requiresAuth) {
        const token = getAuthToken();
        if (!token) {
            logout(); window.location.href = 'login.html';
            throw new Error("Sesión expirada");
        }
        headers['Authorization'] = `Bearer ${token}`;
    }

    try {
        const res = await fetch(url, {
            method, headers, body: body ? JSON.stringify(body) : null
        });
        if (res.status === 204) return { success: true };
        const data = await res.json();
        if (!res.ok) {
            if (res.status === 401 || res.status === 403) { logout(); window.location.href = 'login.html'; }
            throw new Error(data.detail || "Error en API");
        }
        return data;
    } catch (err) {
        console.error(err);
        throw err;
    }
}

// --- Carrito Local ---
let cart = JSON.parse(localStorage.getItem(CART_KEY) || '[]');
function saveCart() { localStorage.setItem(CART_KEY, JSON.stringify(cart)); }
function updateMiniCart() {
    const count = cart.reduce((s, i) => s + (i.quantity || 0), 0);
    const el = document.getElementById('mini-cart-count');
    if(el) el.textContent = count;
}

// Exports
window.apiFetch = apiFetch;
window.getAuthToken = getAuthToken;
window.getLoggedUser = getLoggedUser;
window.saveAuth = saveAuth;
window.logout = logout;
window.cart = cart;
window.saveCart = saveCart;
window.updateMiniCart = updateMiniCart;