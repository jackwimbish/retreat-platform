/**
 * Logo component.
 * Custom logo for Camp Coordinator
 */

import React from 'react';
import { Link } from 'react-router-dom';
import { defineMessages, useIntl } from 'react-intl';
import { Image } from 'semantic-ui-react';
import { useSelector } from 'react-redux';
import { flattenToAppURL } from '@plone/volto/helpers';
import './Logo.css';

const messages = defineMessages({
  site: {
    id: 'Site',
    defaultMessage: 'Site',
  },
  campCoordinator: {
    id: 'Camp Coordinator',
    defaultMessage: 'Camp Coordinator',
  },
});

const Logo = () => {
  const intl = useIntl();
  const site = useSelector((state) => state.site.data);

  return (
    <Link
      to="/"
      aria-label={intl.formatMessage(messages.site)}
      title={intl.formatMessage(messages.site)}
      className="camp-coordinator-logo"
    >
      <div className="logo-container">
        <span className="logo-icon">🏕️</span>
        <div className="logo-text">
          <span className="logo-main">Camp Coordinator</span>
          <span className="logo-tagline">Manage Your Retreat with Ease</span>
        </div>
      </div>
    </Link>
  );
};

export default Logo;