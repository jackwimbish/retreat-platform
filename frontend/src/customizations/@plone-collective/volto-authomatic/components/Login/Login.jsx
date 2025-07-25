/**
 * Login container - Customized to prevent auto-redirect to OIDC
 * @module components/Login/Login
 */
import React, { useEffect, useState } from 'react';
import { authomaticRedirect, listAuthOptions, oidcRedirect } from '@plone-collective/volto-authomatic/actions';
import { injectIntl } from 'react-intl';
import { useSelector, useDispatch } from 'react-redux';
import { useLocation } from 'react-router-dom';
import LoginForm from '@plone-collective/volto-authomatic/components/Login/LoginForm';
import qs from 'query-string';
import { useCookies } from 'react-cookie';

/**
 * Get return url function.
 * @function getReturnUrl
 * @param  {Object} location Location object.
 * @returns {string} Return url.
 */
function getReturnUrl(location) {
  return `${qs.parse(location.search).return_url || (location.pathname === '/login' ? '/' : location.pathname.replace('/login', ''))}`;
}

/**
 * Login function.
 * @function Login
 * @returns {JSX.Element} Markup of the Login page.
 */
function Login({ intl }) {
  const dispatch = useDispatch();
  const [startedOAuth, setStartedOAuth] = useState(false);
  const [startedOIDC, setStartedOIDC] = useState(false);
  const loading = useSelector((state) => state.authOptions.loading);
  const options = useSelector((state) => state.authOptions.options);
  const loginOAuthValues = useSelector((state) => state.authomaticRedirect);
  const loginOIDCValues = useSelector((state) => state.oidcRedirect);
  const location = useLocation();
  const [, setCookie] = useCookies();

  useEffect(() => {
    dispatch(listAuthOptions());
  }, [dispatch]);

  useEffect(() => {
    const next_url = loginOAuthValues.next_url;
    const session = loginOAuthValues.session;
    if (next_url && session && startedOAuth) {
      setStartedOAuth(false);
      // Give time to save state to localstorage
      setTimeout(function () {
        window.location.href = next_url;
      }, 500);
    }
  }, [startedOAuth, loginOAuthValues]);

  const onSelectProvider = (provider) => {
    if (provider.id === 'oidc') {
      setStartedOIDC(true);
      setCookie('return_url', getReturnUrl(location), { path: '/' });
      dispatch(oidcRedirect('oidc'));
    } else {
      setStartedOAuth(true);
      setCookie('return_url', getReturnUrl(location), { path: '/' });
      dispatch(authomaticRedirect(provider.id));
    }
  };

  useEffect(() => {
    const next_url = loginOIDCValues.next_url;
    if (next_url && startedOIDC) {
      setStartedOIDC(false);
      // Give time to save state to localstorage
      setTimeout(function () {
        window.location.href = next_url;
      }, 500);
    }
  }, [startedOIDC, loginOIDCValues]);

  // CUSTOMIZATION: Removed auto-redirect when OIDC is the only option
  // We want users to see both username/password and Google sign-in options
  // The original code would auto-redirect if OIDC was the only auth option
  
  return <LoginForm loading={loading} providers={options} action={'login'} onSelectProvider={onSelectProvider} />;
}

export default injectIntl(Login);