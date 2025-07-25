/**
 * Debug component to check user API structure
 */

import React, { useState } from 'react';
import { useSelector } from 'react-redux';
import { Container, Segment, Header, Button } from 'semantic-ui-react';

const DebugUsers = () => {
  const [userData, setUserData] = useState(null);
  const [singleUser, setSingleUser] = useState(null);
  const [loading, setLoading] = useState(false);
  const token = useSelector((state) => state.userSession.token);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const response = await fetch('/++api++/@users', {
        headers: {
          'Accept': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setUserData(data);
        console.log('Users API response:', data);
        
        // If we have users, fetch details for the first non-admin user
        const users = Array.isArray(data) ? data : (data.items || []);
        const nonAdminUser = users.find(u => u.id !== 'admin' && u.id !== 'Anonymous User');
        
        if (nonAdminUser) {
          // Fetch individual user details
          const userResponse = await fetch(`/++api++/@users/${nonAdminUser.id}`, {
            headers: {
              'Accept': 'application/json',
              'Authorization': `Bearer ${token}`,
            },
          });
          
          if (userResponse.ok) {
            const userDetails = await userResponse.json();
            setSingleUser(userDetails);
            console.log('Single user details:', userDetails);
          }
        }
      } else {
        console.error('Failed to fetch users');
      }
    } catch (err) {
      console.error('Error:', err);
    }
    setLoading(false);
  };

  return (
    <Container>
      <Segment>
        <Header as="h2">Users API Debug</Header>
        <Button primary onClick={fetchUsers} loading={loading}>
          Fetch Users Data
        </Button>
        
        {userData && (
          <Segment>
            <h3>Users List Response:</h3>
            <p><strong>Is Array:</strong> {Array.isArray(userData) ? 'Yes' : 'No'}</p>
            <p><strong>Number of users:</strong> {Array.isArray(userData) ? userData.length : (userData.items ? userData.items.length : 0)}</p>
            
            <h4>First User Structure:</h4>
            <pre>{JSON.stringify(Array.isArray(userData) ? userData[0] : (userData.items ? userData.items[0] : null), null, 2)}</pre>
            
            <details>
              <summary>Full Response</summary>
              <pre>{JSON.stringify(userData, null, 2)}</pre>
            </details>
          </Segment>
        )}
        
        {singleUser && (
          <Segment>
            <h3>Single User Details:</h3>
            <p><strong>ID:</strong> {singleUser.id}</p>
            <p><strong>Has roles field:</strong> {singleUser.roles ? 'Yes' : 'No'}</p>
            <p><strong>Has groups field:</strong> {singleUser.groups ? 'Yes' : 'No'}</p>
            
            <details>
              <summary>Full User Details</summary>
              <pre>{JSON.stringify(singleUser, null, 2)}</pre>
            </details>
          </Segment>
        )}
      </Segment>
    </Container>
  );
};

export default DebugUsers;