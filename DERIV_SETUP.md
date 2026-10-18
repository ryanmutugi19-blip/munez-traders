# Deriv integration setup

The dashboard and `/deriv-market/` page support a public live quote stream for
EUR/USD, GBP/USD, USD/JPY, and BTC/USD. Selecting a market starts its Deriv
tick subscription. The dashboard's chart drawing and order controls remain
practice-only. Set these environment variables in the environment that runs
Django:

- `DERIV_APP_ID`: the application ID registered for this website in Deriv's
  developer tools. Enter it exactly as shown. It is an app identifier, not
  an account token.
- `DERIV_AFFILIATE_URL`: the full HTTPS referral URL issued in your Deriv
  partner account. The redirect only accepts `deriv.com` and its subdomains.

For example, in a local Linux/macOS terminal:

```sh
export DERIV_APP_ID="your_deriv_app_id"
export DERIV_AFFILIATE_URL="https://track.deriv.com/your_partner_link"
python manage.py runserver
```

## Deploying on Render

1. In the Render web service, add `DERIV_APP_ID` with the App ID from Deriv.
   This value may contain letters or numbers; enter it exactly as issued.
2. Make sure the updated project code, especially
   `tradinghub_app/static/js/deriv_market.js`, is committed and pushed to the
   Git branch connected to this Render service.
3. In Render, deploy the latest commit. A Render redeploy without the updated
   commit will continue serving the old static JavaScript bundle.
4. Open `/dashboard/`, force-refresh the page, and read the market-feed status
   below the Markets heading. `Live connection active` confirms the browser
   received a quote. A `Deriv API error: ...` message means the server rejected
   the App ID or selected symbol; use that exact error to troubleshoot.

The dashboard's market section is available after sign-in; `/deriv-market/`
is the standalone quote page. The partner redirect is `/deriv-signup/`.
Without the affiliate URL, the redirect returns an explicit service-unavailable
response. Without an app ID, both market views explain that live prices are
not configured.

This is a public market-data connection only. It does not authorize a Deriv
account, read balances, or place trades. Account access and real trading need
a separately registered and approved authentication flow; never put a
Deriv account token in browser JavaScript or commit it to source control.
