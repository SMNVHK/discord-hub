import React, { useState, useEffect } from 'react';
import { Container, Typography, TextField, Button, Paper, List, ListItem, ListItemText } from '@mui/material';
import { db } from '../services/firebase';
import { ref, push, onChildAdded, query, orderByChild, limitToLast } from "firebase/database";

function DiscordBot() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');

  useEffect(() => {
    const messagesRef = query(ref(db, 'messages'), orderByChild('timestamp'), limitToLast(50));
    const unsubscribe = onChildAdded(messagesRef, (snapshot) => {
      const message = snapshot.val();
      setMessages(prev => [...prev, message].sort((a, b) => a.timestamp - b.timestamp));
    });

    return () => unsubscribe();
  }, []);

  const sendMessage = (e) => {
    e.preventDefault();
    if (input.trim()) {
      const messagesRef = ref(db, 'messages');
      push(messagesRef, {
        text: input,
        sender: 'user',
        userId: 'web_user',
        timestamp: Date.now()
      });
      setInput('');
    }
  };

  return (
    <Container>
      <Typography variant="h2" gutterBottom>
        Discord Bot Interface
      </Typography>
      <Paper style={{ padding: '20px', marginBottom: '20px' }}>
        <Typography variant="h5" gutterBottom>Comment utiliser le bot Discord</Typography>
        <List>
          <ListItem>
            <ListItemText primary="!hub" secondary="Affiche les informations sur le AI Learning Hub" />
          </ListItem>
          <ListItem>
            <ListItemText primary="!quiz" secondary="DÃ©marre un quiz IA interactif" />
          </ListItem>
          <ListItem>
            <ListItemText primary="!delete_history" secondary="Supprime votre historique de conversation" />
          </ListItem>
        </List>
      </Paper>
      <Paper style={{ height: 400, overflowY: 'scroll', marginBottom: 20, padding: 10 }}>
        {messages.map((msg, index) => (
          <Typography key={index} style={{ marginBottom: 10, textAlign: msg.sender === 'user' ? 'right' : 'left' }}>
            <strong>{msg.sender === 'user' ? 'You' : 'Bot'}:</strong> {msg.text}
          </Typography>
        ))}
      </Paper>
      <form onSubmit={sendMessage} style={{ display: 'flex' }}>
        <TextField
          fullWidth
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
        />
        <Button type="submit" variant="contained" color="primary">
          Send
        </Button>
      </form>
    </Container>
  );
}

export default DiscordBot;