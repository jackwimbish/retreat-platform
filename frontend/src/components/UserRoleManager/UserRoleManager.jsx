/**
 * User Role Manager component.
 * Allows admins/directors to manage user roles for the camp
 */

import React, { useState, useEffect } from 'react';
import { Link, useHistory } from 'react-router-dom';
import { useSelector } from 'react-redux';
import {
  Container,
  Segment,
  Header,
  Table,
  Button,
  Icon,
  Label,
  Dropdown,
  Message,
  Loader,
  Input,
  Popup,
} from 'semantic-ui-react';
import { Helmet } from '@plone/volto/helpers';
import { toast } from 'react-toastify';
import { Toast } from '@plone/volto/components';

const UserRoleManager = () => {
  const history = useHistory();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState({});
  const [searchTerm, setSearchTerm] = useState('');
  const [error, setError] = useState(null);
  
  const token = useSelector((state) => state.userSession.token);
  const currentUser = useSelector((state) => state.users?.user);

  // Check if user has permission (admin or Manager role)
  const hasPermission = currentUser?.roles?.includes('Manager') || 
                       currentUser?.roles?.includes('Site Administrator') ||
                       currentUser?.id === 'admin';

  const campRoles = [
    { key: 'member', text: 'Participant', value: 'Member', color: 'blue' },
    { key: 'editor', text: 'Staff', value: 'Editor', color: 'green' },
    { key: 'manager', text: 'Director', value: 'Manager', color: 'purple' },
  ];

  useEffect(() => {
    if (hasPermission) {
      fetchUsers();
    }
  }, [hasPermission]);

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
      const userList = Array.isArray(data) ? data : (data.items || []);
      
      // Filter out system users and fetch detailed info for each user
      const filteredUsers = userList.filter(u => 
        u.id !== 'admin' && u.id !== 'Anonymous User'
      );

      // For each user, determine their camp role
      const usersWithRoles = filteredUsers.map(user => {
        // Determine the highest role level
        let campRole = 'Member'; // Default to Member
        if (user.roles?.includes('Manager')) {
          campRole = 'Manager';
        } else if (user.roles?.includes('Editor')) {
          campRole = 'Editor';
        }
        
        return {
          ...user,
          campRole: campRole,
        };
      });

      setUsers(usersWithRoles);
    } catch (err) {
      console.error('Error fetching users:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const updateUserRole = async (userId, newRole) => {
    setSaving(prev => ({ ...prev, [userId]: true }));
    
    try {
      // Get current user details
      const userResponse = await fetch(`/++api++/@users/${userId}`, {
        headers: {
          'Accept': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!userResponse.ok) {
        throw new Error('Failed to fetch user details');
      }

      const userData = await userResponse.json();
      
      // Build the new roles object
      // Start with keeping existing system roles
      const rolesDict = {};
      
      // Keep system roles like Authenticated, etc.
      userData.roles.forEach(role => {
        if (!['Member', 'Editor', 'Manager'].includes(role)) {
          rolesDict[role] = true;
        }
      });
      
      // Add the selected camp role
      rolesDict[newRole] = true;
      
      // Make the API call with roles as a dict
      const updateResponse = await fetch(`/++api++/@users/${userId}`, {
        method: 'PATCH',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          roles: rolesDict,
        }),
      });

      if (!updateResponse.ok) {
        const errorText = await updateResponse.text();
        console.error('Update failed:', errorText);
        throw new Error('Failed to update user role');
      }

      // Update local state
      setUsers(prev => prev.map(user => 
        user.id === userId ? { ...user, campRole: newRole } : user
      ));

      toast.success(
        <Toast
          success
          title="Role Updated"
          content={`User role updated successfully.`}
        />,
      );

    } catch (err) {
      console.error('Error updating user role:', err);
      toast.error(
        <Toast
          error
          title="Update Failed"
          content={err.message || 'Failed to update user role'}
        />,
      );
    } finally {
      setSaving(prev => ({ ...prev, [userId]: false }));
    }
  };

  // Filter users based on search
  const filteredUsers = users.filter(user => 
    user.fullname?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.id?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // If user doesn't have permission, show access denied
  if (!hasPermission) {
    return (
      <Container>
        <Helmet title="User Management - Access Denied" />
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
      <Helmet title="User Role Management" />
      
      <Segment basic>
        <Header as="h1">
          <Icon name="users" />
          User Role Management
        </Header>
        <p>Manage camp roles for all users. Changes take effect immediately.</p>
      </Segment>

      {error && (
        <Message negative>
          <Message.Header>Error</Message.Header>
          <p>{error}</p>
        </Message>
      )}

      <Segment>
        <Input
          fluid
          icon="search"
          placeholder="Search users by name, email, or username..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </Segment>

      {loading ? (
        <Segment basic>
          <Loader active inline='centered'>
            Loading users...
          </Loader>
        </Segment>
      ) : (
        <Segment>
          <Table celled striped>
            <Table.Header>
              <Table.Row>
                <Table.HeaderCell>User</Table.HeaderCell>
                <Table.HeaderCell>Email</Table.HeaderCell>
                <Table.HeaderCell>Current Role</Table.HeaderCell>
                <Table.HeaderCell>Camp Role</Table.HeaderCell>
              </Table.Row>
            </Table.Header>

            <Table.Body>
              {filteredUsers.map((user) => (
                <Table.Row key={user.id}>
                  <Table.Cell>
                    <strong>{user.fullname || user.id}</strong>
                    <br />
                    <small style={{ color: '#666' }}>@{user.id}</small>
                  </Table.Cell>
                  <Table.Cell>
                    {user.email}
                  </Table.Cell>
                  <Table.Cell>
                    {user.roles?.map(role => (
                      <Label key={role} size="small" basic>
                        {role}
                      </Label>
                    ))}
                  </Table.Cell>
                  <Table.Cell>
                    <Dropdown
                      placeholder="Select Role"
                      selection
                      options={campRoles}
                      value={user.campRole}
                      onChange={(e, { value }) => updateUserRole(user.id, value)}
                      disabled={saving[user.id] || user.id === currentUser?.id}
                      loading={saving[user.id]}
                    />
                    {user.id === currentUser?.id && (
                      <Popup
                        content="You cannot change your own role"
                        trigger={<Icon name="info circle" style={{ marginLeft: '0.5em' }} />}
                      />
                    )}
                  </Table.Cell>
                </Table.Row>
              ))}
            </Table.Body>

            <Table.Footer>
              <Table.Row>
                <Table.HeaderCell colSpan='4'>
                  {filteredUsers.length} user{filteredUsers.length !== 1 ? 's' : ''} found
                </Table.HeaderCell>
              </Table.Row>
            </Table.Footer>
          </Table>

          <Segment basic>
            <Header as="h4">Role Descriptions:</Header>
            <div style={{ marginBottom: '0.5em' }}><Label color="blue">Participant (Member)</Label> Can view and create issues</div>
            <div style={{ marginBottom: '0.5em' }}><Label color="green">Staff (Editor)</Label> Can view, create, and edit all issues</div>
            <div style={{ marginBottom: '0.5em' }}><Label color="purple">Director (Manager)</Label> Full administrative access</div>
          </Segment>
        </Segment>
      )}
    </Container>
  );
};

export default UserRoleManager;