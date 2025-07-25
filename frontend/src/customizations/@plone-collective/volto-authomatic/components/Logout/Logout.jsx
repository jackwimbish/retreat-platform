/**
 * Logout container - Simplified to prevent OIDC logout redirect loop
 * @module components/theme/Logout/Logout
 */

import React, { useEffect } from 'react';
import { Container } from 'semantic-ui-react';
import { defineMessages, injectIntl } from 'react-intl';
import { logout, purgeMessages } from '@plone/volto/actions';
import { useDispatch } from 'react-redux';
import { useHistory } from 'react-router-dom';
import { toast } from 'react-toastify';
import { Toast } from '@plone/volto/components';

const messages = defineMessages({
  loggedOut: {
    id: 'You have been logged out',
    defaultMessage: 'You have been logged out',
  },
});

/**
 * Logout function.
 * @function Logout
 * @returns {JSX.Element} Markup of the Logout page.
 */
function Logout({ intl }) {
  const dispatch = useDispatch();
  const history = useHistory();

  useEffect(() => {
    // Perform regular logout without OIDC redirect
    dispatch(logout());
    dispatch(purgeMessages());
    
    // Show logout message
    toast.info(
      <Toast
        info
        title={intl.formatMessage(messages.loggedOut)}
      />,
    );
    
    // Redirect to home page after a short delay
    setTimeout(() => {
      history.push('/');
    }, 1000);
  }, [dispatch, history, intl]);

  return (
    <div id="page-logout">
      <Container text>{intl.formatMessage(messages.loggedOut)}</Container>
    </div>
  );
}

export default injectIntl(Logout);