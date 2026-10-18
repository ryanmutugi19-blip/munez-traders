(() => {
    const config = document.getElementById("deriv-market-feed")
        || document.getElementById("deriv-market");

    if (!config) {
        return;
    }

    const isDashboard = config.id === "deriv-market-feed";
    const status = document.getElementById(
        isDashboard ? "market-feed-status" : "connection-status"
    );
    const price = document.getElementById(
        isDashboard ? "live-market-price" : "market-price"
    );
    const title = document.getElementById("live-market-title");
    const selector = document.getElementById(
        isDashboard ? "market-select" : "live-market-select"
    );

    if (!status || !price || !selector) {
        console.warn("Deriv market widget is missing required DOM elements.");
        return;
    }

    const appId = config.dataset.appId;
    if (!/^[A-Za-z0-9_-]{1,128}$/.test(appId || "")) {
        status.textContent =
            "Live prices are unavailable: configure a valid Deriv app ID.";
        return;
    }

    if (!("WebSocket" in window)) {
        status.textContent =
            "Live prices are unavailable: this browser does not support WebSocket.";
        return;
    }

    const endpoint =
        `wss://ws.derivws.com/websockets/v3?app_id=${encodeURIComponent(appId)}`;
    let socket;
    let retryDelay = 1000;
    let reconnectTimer;
    let pageIsClosing = false;
    let subscriptionId = null;
    let activeSymbol = null;

    function selectedMarket() {
        const option = selector.selectedOptions && selector.selectedOptions[0];
        if (!option) {
            return { label: "", symbol: "" };
        }

        return {
            label: option.value || "",
            symbol: option.dataset.derivSymbol || "",
        };
    }

    function updateTitle(label) {
        if (title) {
            title.textContent = isDashboard
                ? label.replace("/", " / ")
                : label;
        }
    }

    function connect() {
        if (pageIsClosing) {
            return;
        }

        status.textContent = "Connecting to Deriv live market data...";
        try {
            socket = new WebSocket(endpoint);
        } catch {
            status.textContent =
                "Could not start a Deriv connection. Check the app ID and browser security settings.";
            return;
        }

        socket.addEventListener("open", () => {
            retryDelay = 1000;
            subscribeSelectedMarket();
        });

        socket.addEventListener("message", (event) => {
            let data;
            try {
                data = JSON.parse(event.data);
            } catch {
                status.textContent =
                    "Received an unreadable response from Deriv.";
                return;
            }

            if (data.error) {
                status.textContent =
                    `Deriv API error: ${data.error.message}`;
                return;
            }

            if (data.tick && Number.isFinite(Number(data.tick.quote))) {
                if (data.subscription && data.tick.symbol !== activeSymbol) {
                    socket.send(JSON.stringify({
                        forget: data.subscription.id,
                    }));
                    return;
                }
                if (data.tick.symbol !== activeSymbol) {
                    return;
                }
                if (data.subscription) {
                    subscriptionId = data.subscription.id;
                }
                const precision = Number(data.tick.pip_size);
                const quote = Number(data.tick.quote);
                price.textContent = Number.isInteger(precision)
                    && precision >= 0
                    && precision <= 10
                    ? quote.toFixed(precision)
                    : String(data.tick.quote);
                status.textContent = "Live connection active";
            }
        });

        socket.addEventListener("error", () => {
            status.textContent =
                "Could not connect to Deriv. Retrying...";
        });

        socket.addEventListener("close", () => {
            if (pageIsClosing) {
                return;
            }

            status.textContent = "Connection closed. Retrying...";
            subscriptionId = null;
            activeSymbol = null;
            reconnectTimer = window.setTimeout(connect, retryDelay);
            retryDelay = Math.min(retryDelay * 2, 30000);
        });
    }

    function subscribeSelectedMarket() {
        const market = selectedMarket();
        if (!market.symbol) {
            status.textContent = "No Deriv symbol is configured for this market.";
            return;
        }

        if (socket.readyState !== WebSocket.OPEN) {
            return;
        }

        if (subscriptionId) {
            socket.send(JSON.stringify({ forget: subscriptionId }));
            subscriptionId = null;
        }

        activeSymbol = market.symbol;
        price.textContent = "Waiting for live price...";
        updateTitle(market.label);
        status.textContent = `Subscribing to ${market.label} on Deriv...`;
        socket.send(JSON.stringify({
            ticks: market.symbol,
            subscribe: 1,
        }));
    }

    selector.addEventListener("change", subscribeSelectedMarket);

    window.addEventListener("pagehide", () => {
        pageIsClosing = true;
        window.clearTimeout(reconnectTimer);
        if (socket && socket.readyState < WebSocket.CLOSING) {
            socket.close();
        }
    }, { once: true });

    connect();
})();
