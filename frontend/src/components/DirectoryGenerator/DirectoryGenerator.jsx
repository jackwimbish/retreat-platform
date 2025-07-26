/**
 * Directory Generator component.
 * Allows admins/directors to generate a camp directory document.
 */

import React, { useState } from 'react';
import { useHistory } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { Container, Segment, Header, Button, Icon, Message, Loader } from 'semantic-ui-react';
import { Helmet } from '@plone/volto/helpers';
import { toast } from 'react-toastify';
import { Toast } from '@plone/volto/components';

const DirectoryGenerator = () => {
  const history = useHistory();
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState(null);
  
  const token = useSelector((state) => state.userSession.token);
  const user = useSelector((state) => state.users.user);

  // Check if user has permission (admin or Manager role)
  const hasPermission = user?.roles?.includes('Manager') || user?.['@id']?.includes('/admin');

  const fetchUsers = async () => {
    try {
      const response = await fetch('/++api++/@users', {
        headers: {
          'Accept': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch users');
      }

      const data = await response.json();
      console.log('Users API response:', data);
      
      // The API returns an array directly, not an object with items
      const users = Array.isArray(data) ? data : (data.items || []);
      console.log('Number of users found:', users.length);
      return users;
    } catch (err) {
      console.error('Error fetching users:', err);
      throw err;
    }
  };

  const getInitials = (fullname) => {
    const parts = fullname.split(' ');
    if (parts.length >= 2) {
      return parts[0][0].toUpperCase() + parts[parts.length - 1][0].toUpperCase();
    } else if (parts.length === 1) {
      return parts[0][0].toUpperCase();
    }
    return '?';
  };

  const generateDirectoryHTML = (users) => {
    console.log('Generating HTML for users:', users.length);
    
    // Sort users into categories
    const directors = [];
    const staff = [];
    const participants = [];

    users.forEach(user => {
      // Skip system users
      if (user.id === 'admin' || user.id === 'Anonymous User') return;

      console.log('Processing user:', user.id);
      console.log('  - Full user object:', JSON.stringify(user, null, 2));
      console.log('  - Roles:', user.roles);
      console.log('  - Groups:', user.groups);

      const userInfo = {
        id: user.id,
        fullname: user.fullname || user.id,
        email: user.email || '',
        roles: user.roles || [],
        portrait: user.portrait ? `http://localhost:8080/Plone/@@public-portrait?username=${user.id}` : null,
        initials: getInitials(user.fullname || user.id),
      };

      // Map Plone roles to our camp roles
      if (userInfo.roles.includes('Manager')) {
        console.log(`  -> Adding ${user.id} to directors`);
        directors.push(userInfo);
      } else if (userInfo.roles.includes('Editor')) {
        console.log(`  -> Adding ${user.id} to staff`);
        staff.push(userInfo);
      } else if (userInfo.roles.includes('Member')) {
        console.log(`  -> Adding ${user.id} to participants`);
        participants.push(userInfo);
      } else {
        console.log(`  -> User ${user.id} has no recognized role (roles: ${userInfo.roles.join(', ')}), adding to participants`);
        // Users with no specific role are treated as participants
        participants.push(userInfo);
      }
    });

    console.log('Directors:', directors.length, 'Staff:', staff.length, 'Participants:', participants.length);

    // Sort each group by fullname
    const sortByName = (a, b) => a.fullname.toLowerCase().localeCompare(b.fullname.toLowerCase());
    directors.sort(sortByName);
    staff.sort(sortByName);
    participants.sort(sortByName);

    // Build HTML
    const now = new Date().toLocaleString('en-US', {
      month: 'long',
      day: 'numeric',
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    });

    let html = '<div class="camp-directory">';
    html += `<p class="directory-updated"><em>Last updated: ${now}</em></p>`;

    // Helper function to create section HTML
    const createSection = (title, users, icon) => {
      if (users.length === 0) return '';

      let sectionHtml = '<div class="directory-section">';
      sectionHtml += `<h2>${icon} ${title} <span class="count">(${users.length})</span></h2>`;
      sectionHtml += '<div class="user-grid">';

      users.forEach(user => {
        sectionHtml += '<div class="user-card">';
        
        // Avatar or initials
        if (user.portrait) {
          sectionHtml += `<div class="user-avatar" style="width: 50px; height: 50px; border-radius: 50%; overflow: hidden; flex-shrink: 0;"><img src="${user.portrait}" alt="${user.fullname}" style="width: 50px; height: 50px; object-fit: cover;" /></div>`;
        } else {
          sectionHtml += `<div class="user-avatar initials" style="width: 50px; height: 50px; border-radius: 50%; overflow: hidden; flex-shrink: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 1rem;">${user.initials}</div>`;
        }

        sectionHtml += '<div class="user-info">';
        sectionHtml += `<h3>${user.fullname}</h3>`;
        if (user.email) {
          sectionHtml += `<p class="email"><a href="mailto:${user.email}">${user.email}</a></p>`;
        }
        sectionHtml += '</div></div>';
      });

      sectionHtml += '</div></div>';
      return sectionHtml;
    };

    html += createSection('Directors', directors, '⭐');
    html += createSection('Staff', staff, '🏆');
    html += createSection('Participants', participants, '👥');

    // Add CSS
    html += `
<style>
.camp-directory {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
}
.directory-updated {
    color: #666;
    margin-bottom: 2rem;
}
.directory-section {
    margin-bottom: 3rem;
}
.directory-section h2 {
    color: #333;
    border-bottom: 2px solid #e0e0e0;
    padding-bottom: 0.5rem;
    margin-bottom: 1.5rem;
}
.directory-section .count {
    font-weight: normal;
    color: #666;
    font-size: 0.9em;
}
.user-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1.5rem;
}
.user-card {
    background: #f8f8f8;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    transition: transform 0.2s, box-shadow 0.2s;
}
.user-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
/* Avatar styles are now inline */
.user-info {
    flex-grow: 1;
    min-width: 0;
}
.user-info h3 {
    margin: 0 0 0.25rem 0;
    font-size: 1.1rem;
    color: #333;
}
.user-info .email {
    margin: 0;
    font-size: 0.9rem;
}
.user-info .email a {
    color: #4183c4;
    text-decoration: none;
}
.user-info .email a:hover {
    text-decoration: underline;
}
@media (max-width: 768px) {
    .user-grid {
        grid-template-columns: 1fr;
    }
    .camp-directory {
        padding: 1rem;
    }
}
</style>`;

    html += '</div>';
    return html;
  };

  const handleGenerateDirectory = async () => {
    setIsGenerating(true);
    setError(null);

    try {
      // Fetch all users
      const users = await fetchUsers();
      console.log('Total users fetched:', users.length);
      console.log('User IDs:', users.map(u => u.id));

      // Generate HTML content
      const htmlContent = generateDirectoryHTML(users);
      
      console.log('Generated HTML preview:', htmlContent.substring(0, 200) + '...');

      // Check if directory already exists at the Plone root
      let directoryExists = false;
      let existingDirectory = null;
      
      try {
        // Search for existing directory document
        const searchResponse = await fetch('/++api++/@search?path=/&id=directory', {
          headers: {
            'Accept': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
        });
        
        if (searchResponse.ok) {
          const searchData = await searchResponse.json();
          if (searchData.items && searchData.items.length > 0) {
            existingDirectory = searchData.items[0];
            directoryExists = true;
            console.log('Found existing directory at:', existingDirectory['@id']);
          }
        }
      } catch (err) {
        console.log('Error checking for existing directory:', err);
        directoryExists = false;
      }

      if (directoryExists && existingDirectory) {
        console.log('Directory exists, updating...');
        
        // Convert the URL to API path
        const apiPath = '/++api++' + existingDirectory['@id'].replace('http://localhost:3000', '');
        console.log('Update URL:', apiPath);
        
        // Directory exists, update it with blocks format
        const blockId = 'directory-content-' + Date.now();
        const updateBody = {
          blocks: {
            [blockId]: {
              "@type": "html",
              "html": htmlContent
            }
          },
          blocks_layout: {
            items: [blockId]
          }
        };
        
        console.log('Update body:', JSON.stringify(updateBody).substring(0, 200) + '...');
        
        const updateResponse = await fetch(apiPath, {
          method: 'PATCH',
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
          body: JSON.stringify(updateBody),
        });

        if (!updateResponse.ok) {
          const errorText = await updateResponse.text();
          console.error('Update failed:', errorText);
          throw new Error('Failed to update directory');
        }

        // Check if response has content before parsing
        const responseText = await updateResponse.text();
        if (responseText) {
          try {
            const updateResult = JSON.parse(responseText);
            console.log('Directory updated successfully, result:', updateResult['@id']);
          } catch (e) {
            console.log('Update response was not JSON:', responseText);
          }
        } else {
          console.log('Update completed but no response body');
        }

      } else {
        console.log('Directory does not exist, creating...');
        
        // Directory doesn't exist, create it
        const createResponse = await fetch('/++api++/', {
          method: 'POST',
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
          body: JSON.stringify({
            '@type': 'Document',
            id: 'directory',
            title: 'Camp Directory',
            description: 'Directory of all camp participants, staff, and directors',
            blocks: {
              'directory-content': {
                "@type": "html",
                "html": htmlContent
              }
            },
            blocks_layout: {
              items: ['directory-content']
            },
          }),
        });

        if (!createResponse.ok) {
          const errorData = await createResponse.json();
          console.error('Create failed:', errorData);
          throw new Error(errorData.message || 'Failed to create directory');
        }

        const createdData = await createResponse.json();
        console.log('Directory created at:', createdData['@id']);
      }

      // Wait a moment for the operation to complete
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Try to publish the directory
      try {
        const publishUrl = directoryExists && existingDirectory 
          ? '/++api++' + existingDirectory['@id'].replace('http://localhost:3000', '') + '/@workflow/publish'
          : '/++api++/directory/@workflow/publish';
          
        const publishResponse = await fetch(publishUrl, {
          method: 'POST',
          headers: {
            'Accept': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
        });
        if (publishResponse.ok) {
          console.log('Directory published');
        }
      } catch (err) {
        console.log('Could not publish, might already be published');
      }

      // Show success message
      toast.success(
        <Toast
          success
          title="Directory Generated"
          content="The camp directory has been updated successfully."
        />,
      );

      // Redirect to the directory and force reload
      setTimeout(() => {
        window.location.href = '/directory';
      }, 1000);

    } catch (err) {
      console.error('Error generating directory:', err);
      setError(err.message || 'Failed to generate directory');
      toast.error(
        <Toast
          error
          title="Generation Failed"
          content={err.message || 'Failed to generate directory'}
        />,
      );
    } finally {
      setIsGenerating(false);
    }
  };

  // If user doesn't have permission, show access denied
  if (!hasPermission) {
    return (
      <Container>
        <Helmet title="Directory Generator - Access Denied" />
        <Segment basic padded="very" textAlign="center">
          <Header as="h2" icon>
            <Icon name="lock" />
            Access Denied
            <Header.Subheader>
              Only administrators and directors can access this page.
            </Header.Subheader>
          </Header>
        </Segment>
      </Container>
    );
  }

  return (
    <Container>
      <Helmet title="Directory Generator" />
      
      <Segment basic textAlign="center">
        <Header as="h1">
          <Icon name="users" />
          Camp Directory Generator
        </Header>
        <p>Generate or update the camp directory with current user information.</p>
      </Segment>

      <Segment padded="very" textAlign="center">
        {error && (
          <Message negative>
            <Message.Header>Error</Message.Header>
            <p>{error}</p>
          </Message>
        )}

        <p>
          Click the button below to generate a directory of all camp participants,
          staff, and directors. This will create or update the directory page
          with the latest user information.
        </p>

        <Button
          primary
          size="large"
          onClick={handleGenerateDirectory}
          disabled={isGenerating}
          loading={isGenerating}
        >
          <Icon name="refresh" />
          {isGenerating ? 'Generating Directory...' : 'Generate Directory'}
        </Button>

        {isGenerating && (
          <Segment basic>
            <Loader active inline='centered'>
              Fetching users and creating directory...
            </Loader>
          </Segment>
        )}
      </Segment>
    </Container>
  );
};

export default DirectoryGenerator;