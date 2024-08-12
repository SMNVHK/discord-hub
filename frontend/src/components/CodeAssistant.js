import React, { useState } from 'react';
import { Container, Typography, TextField, Button, Paper } from '@mui/material';

function CodeAssistant() {
  const [code, setCode] = useState('');
  const [suggestion, setSuggestion] = useState('');

  const handleCodeChange = (event) => {
    setCode(event.target.value);
  };

  const handleGetSuggestion = () => {
    // In a real application, this would call an AI service to get suggestions
    setSuggestion("Here's a suggestion for your code:\n\n// Add error handling\ntry {\n  // Your code here\n} catch (error) {\n  console.error('An error occurred:', error);\n}");
  };

  return (
    <Container>
      <Typography variant="h2" gutterBottom>
        AI Code Assistant
      </Typography>
      <Typography variant="body1" paragraph>
        Enter your code below and get AI-powered suggestions!
      </Typography>
      <TextField
        fullWidth
        multiline
        rows={10}
        variant="outlined"
        value={code}
        onChange={handleCodeChange}
        placeholder="Enter your code here..."
        margin="normal"
      />
      <Button variant="contained" color="primary" onClick={handleGetSuggestion}>
        Get Suggestion
      </Button>
      {suggestion && (
        <Paper style={{ marginTop: 20, padding: 20 }}>
          <Typography variant="h6" gutterBottom>
            Suggestion:
          </Typography>
          <pre>{suggestion}</pre>
        </Paper>
      )}
    </Container>
  );
}

export default CodeAssistant;