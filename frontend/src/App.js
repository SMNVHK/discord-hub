import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

import Navbar from './components/Navbar';
import Home from './components/Home';
import Quests from './components/Quests';
import AILab from './components/AILab';
import Quiz from './components/Quiz';
import CodeAssistant from './components/CodeAssistant';
import Brainstorm from './components/Brainstorm';
import DiscordBot from './components/DiscordBot';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Navbar />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/quests" element={<Quests />} />
          <Route path="/ailab" element={<AILab />} />
          <Route path="/quiz" element={<Quiz />} />
          <Route path="/code-assistant" element={<CodeAssistant />} />
          <Route path="/brainstorm" element={<Brainstorm />} />
          <Route path="/discord-bot" element={<DiscordBot />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;