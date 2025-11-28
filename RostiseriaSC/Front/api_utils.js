const API_BASE_URL = "http://127.0.0.1:8000";
const K_AUTH = "rostiseria_auth";
const K_CART = "rostiseria_cart";

function saveAuth(token, email, isAdmin) { localStorage.setItem(K_AUTH, JSON.stringify({token, email, isAdmin})); }
function getAuth() { try { return JSON.parse(localStorage.getItem(K_AUTH)); } catch { return null; } }
function getLoggedUser() { const a = getAuth(); return a ? {email: a.email, isAdmin: !!a.isAdmin} : null; }
function clearAuth() { localStorage.removeItem(K_AUTH); }

async function apiFetch(path, method="GET", body=null, auth=false) {
    const headers = {"Content-Type": "application/json"};
    if(auth) {
        const s = getAuth();
        if(!s) throw new Error("Sin sesión");
        headers["Authorization"] = `Bearer ${s.token}`;
    }
    const res = await fetch(API_BASE_URL + path, { method, headers, body: body ? JSON.stringify(body) : null });
    if(!res.ok) {
        const err = await res.json().catch(()=>({}));
        throw new Error(err.detail || `Error ${res.status}`);
    }
    return res.status===204 ? null : await res.json();
}

function getCart() { try { return JSON.parse(localStorage.getItem(K_CART)) || []; } catch { return []; } }
function saveCart(c) { localStorage.setItem(K_CART, JSON.stringify(c)); }
function clearCart() { localStorage.removeItem(K_CART); }
function addToCart(p) {
    const c = getCart();
    const idx = c.findIndex(i => i.id === p.id);
    if(idx>=0) c[idx].quantity += (p.quantity||1);
    else c.push({...p, quantity: p.quantity||1});
    saveCart(c);
}