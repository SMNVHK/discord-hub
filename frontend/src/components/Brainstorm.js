import React, { useState } from 'react';
import { Container, Typography, TextField, Button, List, ListItem, ListItemText, Paper } from '@mui/material';

function Brainstorm() {
  const [ideas, setIdeas] = useState([]);
  const [newIdea, setNewIdea] = useState('');

  const handleNewIdeaChange = (event) => {
    setNewIdea(event.target.value);
  };

  const handleAddIdea = () => {
    if (newIdea.trim() !== '') {
      setIdeas([...ideas, newIdea]);
      setNewIdea('');
    }
  };

  return (
    <Container>
      <Typography variant="h2" gutterBottom>
        AI Project Brainstorming
      </Typography>
      <Typography variant="body1" paragraph>
        Share your ideas for AI projects and get inspired by others!
      </Typography>
      <TextField
        fullWidth
        variant="outlined"
        value={newIdea}
        onChange={handleNewIdeaChange}
        placeholder="Enter your idea..."
        margin="normal"
      />
      <Button variant="contained" color="primary" onClick={handleAddIdea}>
        Add Idea
      </Button>
      <Paper style={{ marginTop: 20, padding: 20 }}>
        <Typography variant="h6" gutterBottom>
          Ideas:
        </Typography>
        <List>
          {ideas.map((idea, index) => (
            <ListItem key={index}>
              <ListItemText primary={idea} />
            </ListItem>
          ))}
        </List>
      </Paper>
    </Container>
  );
}

export default Brainstorm;