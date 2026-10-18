from django.core.exceptions import ImproperlyConfigured
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse


class DerivIntegrationTests(TestCase):
    @override_settings(DERIV_AFFILIATE_URL='')
    def test_signup_route_reports_missing_partner_configuration(self):
        response = self.client.get(reverse('deriv_signup'))

        self.assertEqual(response.status_code, 503)
        self.assertContains(
            response,
            'Deriv partner signup is not configured yet.',
            status_code=503,
        )

    @override_settings(
        DERIV_AFFILIATE_URL='https://track.deriv.com/_abc123'
    )
    def test_signup_route_redirects_to_configured_deriv_partner_url(self):
        response = self.client.get(reverse('deriv_signup'))

        self.assertRedirects(
            response,
            'https://track.deriv.com/_abc123',
            fetch_redirect_response=False,
        )

    @override_settings(DERIV_AFFILIATE_URL='http://deriv.com/signup')
    def test_signup_route_rejects_non_https_partner_urls(self):
        with self.assertRaises(ImproperlyConfigured):
            self.client.get(reverse('deriv_signup'))

    @override_settings(DERIV_APP_ID='12345', DERIV_AFFILIATE_URL='')
    def test_market_page_uses_configured_public_app_id(self):
        user = get_user_model().objects.create_user(
            username='deriv-test-user',
            password='test-password',
        )
        self.client.force_login(user)
        response = self.client.get(reverse('deriv_market'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-app-id="12345"')
        self.assertContains(response, 'src="/static/js/deriv_market.js"')
        self.assertContains(response, 'Public market data only.')
        self.assertContains(response, 'id="live-market-select"')

    @override_settings(DERIV_APP_ID='12345')
    def test_dashboard_uses_deriv_live_market_feed(self):
        user = get_user_model().objects.create_user(
            username='deriv-dashboard-user',
            password='test-password',
        )
        self.client.force_login(user)
        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="deriv-market-feed"')
        self.assertContains(response, 'data-app-id="12345"')
        self.assertContains(response, 'id="live-market-price"')
        self.assertContains(response, 'src="/static/js/deriv_market.js"')
        self.assertContains(response, 'practice-only')
        self.assertContains(response, 'data-deriv-symbol="frxEURUSD"')
        self.assertContains(response, 'data-deriv-symbol="cryBTCUSD"')

    @override_settings(DERIV_AFFILIATE_URL='https://track.deriv.com/_abc123')
    def test_public_login_page_exposes_partner_signup_link(self):
        response = self.client.get(reverse('login'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse('deriv_signup'))
