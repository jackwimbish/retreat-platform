/**
 * Custom Login component that shows both username/password and Google sign-in
 */
import React, { useEffect } from 'react';
import { useHistory, useLocation } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { Container, Segment, Grid, Button } from 'semantic-ui-react';
import { FormattedMessage, defineMessages, injectIntl } from 'react-intl';
import { Helmet } from '@plone/volto/helpers';
import { login } from '@plone/volto/actions';
import { toast } from 'react-toastify';
import { Toast } from '@plone/volto/components';
import qs from 'query-string';
import { LoginForm } from '@plone/volto/components';
import { listAuthOptions } from '@plone-collective/volto-authomatic/actions';

const messages = defineMessages({
  login: {
    id: 'Log in',
    defaultMessage: 'Log in',
  },
  loginFailed: {
    id: 'Login failed',
    defaultMessage: 'Login failed',
  },
  loginSuccess: {
    id: 'You are now logged in',
    defaultMessage: 'You are now logged in',
  },
  orLoginWith: {
    id: 'Or log in with',
    defaultMessage: 'Or log in with',
  },
});

const Login = ({ intl }) => {
  const history = useHistory();
  const location = useLocation();
  const dispatch = useDispatch();
  const token = useSelector((state) => state.userSession.token);
  const loading = useSelector((state) => state.userSession.loading);
  const error = useSelector((state) => state.userSession.error);
  const authOptions = useSelector((state) => state.authOptions?.options || []);

  useEffect(() => {
    dispatch(listAuthOptions());
  }, [dispatch]);

  useEffect(() => {
    if (token) {
      const nextUrl = qs.parse(location.search).return_url || '/';
      history.push(nextUrl);
      toast.success(
        <Toast
          success
          title={intl.formatMessage(messages.loginSuccess)}
        />,
      );
    }
  }, [token, history, location.search, intl]);

  useEffect(() => {
    if (error) {
      toast.error(
        <Toast
          error
          title={intl.formatMessage(messages.loginFailed)}
          content={error.message}
        />,
      );
    }
  }, [error, intl]);

  const onLogin = (username, password) => {
    dispatch(login(username, password));
  };

  const onGoogleLogin = () => {
    const returnUrl = qs.parse(location.search).return_url || '/';
    // Save return URL in cookie for volto-authomatic
    document.cookie = `return_url=${encodeURIComponent(returnUrl)}; path=/`;
    // Redirect to OIDC login
    window.location.href = '/@@oidc-login';
  };

  return (
    <div id="page-login">
      <Helmet title={intl.formatMessage(messages.login)} />
      <Container text>
        <Grid textAlign="center" style={{ height: '100vh' }} verticalAlign="middle">
          <Grid.Column style={{ maxWidth: 450 }}>
            <h1 className="documentFirstHeading">
              <FormattedMessage id="Log in" defaultMessage="Log in" />
            </h1>
            
            {/* Standard login form */}
            <LoginForm
              onSubmit={onLogin}
              loading={loading}
            />

            {/* Google Sign-in option */}
            {authOptions.some(opt => opt.id === 'oidc') && (
              <Segment>
                <p style={{ margin: '1em 0' }}>
                  <FormattedMessage id="Or log in with" defaultMessage="Or log in with" />
                </p>
                <Button
                  color="red"
                  fluid
                  size="large"
                  onClick={onGoogleLogin}
                  icon="google"
                  content="Sign in with Google"
                />
              </Segment>
            )}
          </Grid.Column>
        </Grid>
      </Container>
    </div>
  );
};

export default injectIntl(Login);