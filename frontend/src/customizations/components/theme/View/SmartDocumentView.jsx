/**
 * Smart Document View - automatically uses Issues Dashboard if document contains issues
 */

import React from 'react';
import DefaultView from '@plone/volto/components/theme/View/DefaultView';
import IssuesFolderView from './IssuesFolderView';

const SmartDocumentView = (props) => {
  const { content } = props;
  
  // Check if this document contains any issues
  const hasIssues = content.items?.some(item => item['@type'] === 'issue');
  
  // If it contains issues, use the Issues Dashboard view
  if (hasIssues) {
    return <IssuesFolderView {...props} />;
  }
  
  // Otherwise use the default document view
  return <DefaultView {...props} />;
};

export default SmartDocumentView;