// ==========================================
// E.TRADERS - MAIN JAVASCRIPT
// ==========================================


// 1. CHECK WEBSITE
console.log("E.Traders JavaScript loaded!");


// ==========================================
// 2. PASSWORD SHOW / HIDE
// ==========================================

const togglePassword = document.getElementById("togglePassword");
const passwordInput = document.getElementById("password");

if (togglePassword && passwordInput) {

    togglePassword.addEventListener("click", function () {

        if (passwordInput.type === "password") {

            passwordInput.type = "text";
            togglePassword.textContent = "🙈";

        } else {

            passwordInput.type = "password";
            togglePassword.textContent = "👁";

        }

    });

}


// ==========================================
// 3. LOGIN FORM
// ==========================================

const loginForm = document.getElementById("loginForm");

if (loginForm) {

    loginForm.addEventListener("submit", function (event) {

        event.preventDefault();

        alert(
            "The login page is ready for backend connection."
        );

    });

}


// ==========================================
// 4. REGISTRATION FORM
// ==========================================

const registerForm = document.getElementById("registerForm");

if (registerForm) {

    registerForm.addEventListener("submit", function (event) {

        event.preventDefault();

        const password =
            document.getElementById("registerPassword").value;

        const confirmPassword =
            document.getElementById("confirmPassword").value;

        if (password !== confirmPassword) {

            alert("Your passwords do not match.");

            return;

        }

        alert(
            "Registration form checked! A secure backend is needed to create your account."
        );

    });

}


// ==========================================
// 5. LANDING PAGE MARKET CARDS
// ==========================================

const marketCards = document.querySelectorAll(".market-card");

marketCards.forEach(function (card) {

    card.addEventListener("click", function () {

        const marketName =
            card.querySelector("h3").textContent;

        console.log("Selected market:", marketName);

    });

});


// ==========================================
// 6. DEMO NAVIGATION MESSAGE
// ==========================================

const viewStrategyLinks =
    document.querySelectorAll(".strategy-card a");

viewStrategyLinks.forEach(function (link) {

    link.addEventListener("click", function (event) {

        if (link.getAttribute("href") === "#") {

            event.preventDefault();

            alert(
                "Strategy details will be added in a future update."
            );

        }

    });

});


// ==========================================
// 7. PAGE READY MESSAGE
// ==========================================

document.addEventListener("DOMContentLoaded", function () {

    console.log("E.Traders page is ready.");

});

// ========================================
// DERIV API CONNECTION
// ========================================

const derivConnection = new WebSocket(
    "wss://ws.binaryws.com/websockets/v3"
);

// When the connection opens
derivConnection.addEventListener("open", function () {

    console.log("Connected to Deriv!");

    // Request a live price stream
    derivConnection.send(JSON.stringify({
        ticks: "1HZ100V",
        subscribe: 1
    }));

});

// Receive data from Deriv
derivConnection.addEventListener("message", function (event) {

    const data = JSON.parse(event.data);

    if (data.error) {
        console.error("Deriv error:", data.error.message);
        return;
    }

    if (data.msg_type === "tick") {

        console.log(
            "Volatility 100 price:",
            data.tick.quote
        );

    }

});

// Handle connection errors
derivConnection.addEventListener("error", function () {

    console.error("Could not connect to Deriv.");

});

// When the connection closes
derivConnection.addEventListener("close", function () {

    console.log("Deriv connection closed.");

});