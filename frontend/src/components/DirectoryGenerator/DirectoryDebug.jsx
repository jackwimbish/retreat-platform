/**
 * Debug component to check directory content
 */

import React, { useState, useEffect } from 'react';
import { useSelector } from 'react-redux';
import { Container, Segment, Header, Button } from 'semantic-ui-react';

const DirectoryDebug = () => {
  const [directoryData, setDirectoryData] = useState(null);
  const [loading, setLoading] = useState(false);
  const token = useSelector((state) => state.userSession.token);

  const fetchDirectory = async () => {
    setLoading(true);
    try {
      const response = await fetch('/++api++/directory', {
        headers: {
          'Accept': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setDirectoryData(data);
        console.log('Directory data:', data);
      } else {
        console.error('Failed to fetch directory');
      }
    } catch (err) {
      console.error('Error:', err);
    }
    setLoading(false);
  };

  return (
    <Container>
      <Segment>
        <Header as="h2">Directory Debug</Header>
        <Button primary onClick={fetchDirectory} loading={loading}>
          Fetch Directory Data
        </Button>
        
        {directoryData && (
          <Segment>
            <h3>Directory Content:</h3>
            <p><strong>Title:</strong> {directoryData.title}</p>
            <p><strong>Description:</strong> {directoryData.description}</p>
            <p><strong>Text field exists:</strong> {directoryData.text ? 'Yes' : 'No'}</p>
            {directoryData.text && (
              <>
                <p><strong>Text content-type:</strong> {directoryData.text['content-type']}</p>
                <p><strong>Text data length:</strong> {directoryData.text.data ? directoryData.text.data.length : 0}</p>
                <details>
                  <summary>Raw text data (first 500 chars)</summary>
                  <pre>{directoryData.text.data ? directoryData.text.data.substring(0, 500) : 'No data'}</pre>
                </details>
              </>
            )}
            <details>
              <summary>Full JSON</summary>
              <pre>{JSON.stringify(directoryData, null, 2)}</pre>
            </details>
          </Segment>
        )}
      </Segment>
    </Container>
  );
};

export default DirectoryDebug;