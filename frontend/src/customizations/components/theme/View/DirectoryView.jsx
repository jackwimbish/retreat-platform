/**
 * Directory View component.
 * Custom view for the Camp Directory with admin controls
 */

import React from 'react';
import { Link } from 'react-router-dom';
import { useSelector } from 'react-redux';
import {
  Container,
  Button,
  Icon,
  Segment,
  Divider,
} from 'semantic-ui-react';
import RenderBlocks from '@plone/volto/components/theme/View/RenderBlocks';
import { hasBlocksData } from '@plone/volto/helpers';

const DirectoryView = (props) => {
  const { content } = props;
  const currentUser = useSelector((state) => state.users?.user);
  
  // Check if user has permission (admin or Manager role)
  // Only admins and users with Manager role should see the button
  const hasPermission = currentUser?.roles?.includes('Manager') || 
                       currentUser?.roles?.includes('Site Administrator') ||
                       currentUser?.id === 'admin';

  return (
    <Container id="page-document">
      {/* Admin controls */}
      {hasPermission && (
        <Segment basic clearing style={{ paddingBottom: 0 }}>
          <Button 
            as={Link} 
            to="/directory-generator" 
            primary 
            floated="right"
            icon
            labelPosition="left"
          >
            <Icon name="refresh" />
            Update Directory
          </Button>
        </Segment>
      )}
      
      {/* Directory content */}
      {hasBlocksData(content) && (
        <RenderBlocks {...props} />
      )}
    </Container>
  );
};

export default DirectoryView;