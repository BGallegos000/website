const API_BASE_URL = "http://127.0.0.1:8000";
const K_AUTH = "rostiseria_auth";
const K_CART = "rostiseria_cart";
// --- GESTIÓN DE AUTENTICACIÓN ---
function saveAuth(token, email, isAdmin) { localStorage.setItem(K_AUTH, JSON.stringify({token, email, isAdmin})); }
function getAuth() { try { return JSON.parse(localStorage.getItem(K_AUTH)); } catch { return null; } }
function getLoggedUser() { const a = getAuth(); return a ? {email: a.email, isAdmin: !!a.isAdmin} : null; }
function clearAuth() { localStorage.removeItem(K_AUTH); }

// --- UTILIDADES DE API ---
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

// --- GESTIÓN DEL CARRITO DE COMPRAS ---
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

// --- FUNCIÓN CENTRALIZADA DEL NAVBAR  ---
function configurarNavbar() {
    const user = getLoggedUser();
    if (!user) return; // Si no hay usuario, no hacemos nada

    // 1. Mostrar Admin si corresponde
    const navAdmin = document.getElementById("navAdminItem");
    if (user.isAdmin && navAdmin) {
        navAdmin.classList.remove("d-none");
    }

    // 2. "Mis Pedidos" 
    const dropdownMenu = document.querySelector(".dropdown-menu");
    // Verificamos que exista el menú y que no hayamos agregado el botón antes
    if (dropdownMenu && !dropdownMenu.innerHTML.includes("mis_pedidos.html")) {
        const li = document.createElement("li");
        li.innerHTML = `<a class="dropdown-item fw-bold text-primary" href="mis_pedidos.html"><i class="bi bi-receipt me-2"></i>Mis Pedidos</a>`;
        
        // Insertar al principio del menú
        dropdownMenu.prepend(li); 
    }

    // 3. Cambiar Login por Logout
    const loginContainer = document.getElementById("navLoginContainer");
    const mobileLogin = document.getElementById("mobileLoginLink");
    const logoutAction = (e) => {
        e.preventDefault();
        clearAuth();
        window.location.href = "index.html";
    };
// Actualizar el contenedor de login
    if (loginContainer) {
        loginContainer.innerHTML = `<a class="nav-link mx-2 text-warning" href="#" id="btnLogoutGlobal"><i class="bi bi-person-circle me-1"></i>Salir</a>`;
        document.getElementById("btnLogoutGlobal").addEventListener("click", logoutAction);
    }
    // Actualizar el enlace móvil de login
    if (mobileLogin) {
        mobileLogin.textContent = "Cerrar Sesión";
        mobileLogin.addEventListener("click", logoutAction);
    }
}