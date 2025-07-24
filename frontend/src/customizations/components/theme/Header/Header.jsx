import { Container, Segment } from 'semantic-ui-react';
import PropTypes from 'prop-types';
import { useSelector, shallowEqual } from 'react-redux';

import {
  Anontools,
  LanguageSelector,
  Logo,
  Navigation,
  SearchWidget,
} from '@plone/volto/components';
import QuickIssueModal from '../../../../components/QuickIssueModal';

const Header = ({ pathname }) => {
  const token = useSelector((state) => state.userSession.token, shallowEqual);

  return (
    <Segment basic className="header-wrapper" role="banner">
      <Container>
        <div className="header">
          <div className="logo-nav-wrapper">
            <div className="logo">
              <Logo />
            </div>
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
