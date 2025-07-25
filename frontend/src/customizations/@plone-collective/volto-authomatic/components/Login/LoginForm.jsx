/**
 * Login form customized to show both standard login and Google sign-in
 * @module components/LoginForm/LoginForm
 */
import React from 'react';
import { Helmet } from '@plone/volto/helpers';
import { Container, Segment, Button, Form, Message } from 'semantic-ui-react';
import { FormattedMessage, defineMessages, injectIntl } from 'react-intl';
import { login } from '@plone/volto/actions';
import { useDispatch, useSelector } from 'react-redux';
import { useHistory, useLocation } from 'react-router-dom';
import { toast } from 'react-toastify';
import { Toast } from '@plone/volto/components';
import qs from 'query-string';

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
  username: {
    id: 'Username',
    defaultMessage: 'Username',
  },
  password: {
    id: 'Password',
    defaultMessage: 'Password',
  },
  cancel: {
    id: 'Cancel',
    defaultMessage: 'Cancel',
  },
  forgotPassword: {
    id: 'Forgot your password?',
    defaultMessage: 'Forgot your password?',
  },
  orLoginWith: {
    id: 'Or log in with',
    defaultMessage: 'Or log in with',
  },
});

/**
 * Login function.
 * @function LoginForm
 * @returns {JSX.Element} Markup of the Login page.
 */
function LoginForm({ intl, loading, providers, action, onSelectProvider }) {
  const dispatch = useDispatch();
  const history = useHistory();
  const location = useLocation();
  const [isLoading, setIsLoading] = React.useState(false);
  const [username, setUsername] = React.useState('');
  const [password, setPassword] = React.useState('');
  
  const token = useSelector((state) => state.userSession.token);
  const loginError = useSelector((state) => state.userSession.error);

  React.useEffect(() => {
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

  React.useEffect(() => {
    if (loginError) {
      setIsLoading(false);
      toast.error(
        <Toast
          error
          title={intl.formatMessage(messages.loginFailed)}
          content={loginError.message}
        />,
      );
    }
  }, [loginError, intl]);

  const onSubmit = (e) => {
    e.preventDefault();
    setIsLoading(true);
    dispatch(login(username, password));
  };

  const onCancel = () => {
    history.push('/');
  };

  const hasOIDC = providers.some(p => p.id === 'oidc');

  return (
    <div id="page-login">
      <Helmet title={intl.formatMessage(messages.login)} />
      <Container text>
        <Segment.Group raised>
          <Segment className="primary">
            <FormattedMessage id="Log In" defaultMessage="Login" />
          </Segment>
          
          <Segment className="form">
            <Form onSubmit={onSubmit}>
              <Form.Field>
                <label htmlFor="login-username">
                  {intl.formatMessage(messages.username)}
                </label>
                <input
                  id="login-username"
                  name="username"
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                />
              </Form.Field>
              
              <Form.Field>
                <label htmlFor="login-password">
                  {intl.formatMessage(messages.password)}
                </label>
                <input
                  id="login-password"
                  name="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </Form.Field>

              <Form.Field>
                <Button 
                  primary 
                  type="submit" 
                  loading={isLoading}
                  disabled={isLoading || !username || !password}
                  fluid
                >
                  {intl.formatMessage(messages.login)}
                </Button>
              </Form.Field>

              <Form.Field>
                <Button 
                  basic 
                  type="button"
                  onClick={onCancel}
                  fluid
                >
                  {intl.formatMessage(messages.cancel)}
                </Button>
              </Form.Field>
            </Form>

            <Message>
              <a href="/@@request-password-reset">
                {intl.formatMessage(messages.forgotPassword)}
              </a>
            </Message>

            {hasOIDC && (
              <>
                <div className="ui horizontal divider">
                  {intl.formatMessage(messages.orLoginWith)}
                </div>
                
                <Button
                  color="red"
                  fluid
                  size="large"
                  onClick={() => onSelectProvider({ id: 'oidc' })}
                  icon="google"
                  content="Sign in with Google"
                />
              </>
            )}
          </Segment>
        </Segment.Group>
      </Container>
    </div>
  );
}

export default injectIntl(LoginForm);