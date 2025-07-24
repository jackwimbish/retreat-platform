import React, { useEffect } from 'react';
import { Container, Segment } from 'semantic-ui-react';
import PropTypes from 'prop-types';
import { useSelector, useDispatch, shallowEqual } from 'react-redux';
import jwtDecode from 'jwt-decode';
import { getUser } from '@plone/volto/actions';

import {
  Anontools,
  LanguageSelector,
  Logo,
  Navigation,
  SearchWidget,
} from '@plone/volto/components';
import QuickIssueModal from '../../../../components/QuickIssueModal';
import './Header.css';

const Header = ({ pathname }) => {
  const dispatch = useDispatch();
  const token = useSelector((state) => state.userSession.token, shallowEqual);
  const user = useSelector((state) => state.users.user);
  
  useEffect(() => {
    if (token && !user?.id) {
      const userId = jwtDecode(token).sub;
      dispatch(getUser(userId));
    }
  }, [token, user, dispatch]);

  return (
    <Segment basic className="header-wrapper" role="banner">
      <Container>
        <div className="header">
          <div className="logo-nav-wrapper">
            <div className="logo">
              <Logo />
            </div>
            {token && user && (
              <div className="user-info">
                <span className="username">
                  {user.fullname || user.username || user.id}
                </span>
              </div>
            )}
            <Navigation pathname={pathname} />
          </div>
          <div className="tools-search-wrapper">
            <LanguageSelector />
            {!token && (
              <div className="tools">
                <Anontools />
              </div>
            )}
            {token && (
              <div className="quick-issue-button">
                <QuickIssueModal headerMode />
              </div>
            )}
            <div className="search">
              <SearchWidget />
            </div>
          </div>
        </div>
      </Container>
    </Segment>
  );
};

export default Header;

Header.propTypes = {
  token: PropTypes.string,
  pathname: PropTypes.string.isRequired,
  content: PropTypes.objectOf(PropTypes.any),
};

Header.defaultProps = {
  token: null,
  content: null,
};
