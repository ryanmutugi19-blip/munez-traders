// deriv.js - Centralized Deriv API & Authentication Helper

// Replace '1089' with your actual App ID from the Deriv Developer Portal (1089 is a public test ID)
const APP_ID = '1089'; 
let ws = null;

/**
 * Initialize or return the active global WebSocket connection
 */
function getDerivSocket() {
    if (!ws || ws.readyState === WebSocket.CLOSED || ws.readyState === WebSocket.CLOSING) {
        ws = new WebSocket(`wss://ws.derivws.com/websockets/v3?app_id=${APP_ID}`);
        
        ws.onclose = () => {
            console.warn('Deriv WebSocket closed. Reconnecting...');
            setTimeout(getDerivSocket, 3000);
        };

        ws.onerror = (error) => {
            console.error('Deriv WebSocket Error:', error);
        };
    }
    return ws;
}

/**
 * Retrieve stored user token and account ID from browser localStorage
 */
function getStoredAccount() {
    const token = localStorage.getItem('deriv_token');
    const acct = localStorage.getItem('deriv_acct');
    return token ? { token, acct } : null;
}

/**
 * Authorize the user session using their stored token
 * @param {Function} callback - Function called with authorization response data
 */
function authorizeSession(callback) {
    const socket = getDerivSocket();
    const account = getStoredAccount();

    if (!account) {
        if (callback) callback({ error: 'No token found' });
        return;
    }

    const sendAuth = () => {
        socket.send(JSON.stringify({ authorize: account.token }));
    };

    if (socket.readyState === WebSocket.OPEN) {
        sendAuth();
    } else {
        socket.onopen = sendAuth;
    }

    // Listen for authorization response
    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.msg_type === 'authorize') {
            if (callback) callback(data);
        }
    };
}

/**
 * Redirect user to Deriv's official OAuth login page 
 * and specify loadingpage.html as the return callback URL
 */
function redirectToDerivLogin() {
    // Dynamically builds the redirect URL based on your current domain/host
    const redirectUrl = window.location.origin + '/loadingpage.html'; 
    window.location.href = `https://oauth.deriv.com/oauth2/authorize?app_id=${APP_ID}&l=EN&brand=deriv`;
}

/**
 * Log out user by clearing storage and reloading the login page
 */
function logoutDeriv() {
    localStorage.removeItem('deriv_token');
    localStorage.removeItem('deriv_acct');
    window.location.href = '/login.html';
}