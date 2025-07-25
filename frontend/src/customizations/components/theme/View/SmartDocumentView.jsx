/**
 * Smart Document View - automatically uses custom views based on content
 */

import React from 'react';
import DefaultView from '@plone/volto/components/theme/View/DefaultView';
import IssuesFolderView from './IssuesFolderView';
import DirectoryView from './DirectoryView';

const SmartDocumentView = (props) => {
  const { content } = props;
  
  console.log('SmartDocumentView - content.id:', content.id);
  console.log('SmartDocumentView - content.title:', content.title);
  console.log('SmartDocumentView - content[@type]:', content['@type']);
  
  // Check if this is the directory document
  if (content.id === 'directory' || content.title === 'Camp Directory') {
    console.log('Using DirectoryView for directory');
    return <DirectoryView {...props} />;
  }
  
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