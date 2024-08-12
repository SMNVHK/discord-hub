import React from 'react';
   import { AppBar, Toolbar, Typography, Button } from '@mui/material';
   import { Link } from 'react-router-dom';

   function Navbar() {
     return (
       <AppBar position="static">
         <Toolbar>
           <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
             Hub d'Apprentissage IA
           </Typography>
           <Button color="inherit" component={Link} to="/">Accueil</Button>
           <Button color="inherit" component={Link} to="/quests">Quêtes</Button>
           <Button color="inherit" component={Link} to="/ailab">Labo IA</Button>
           <Button color="inherit" component={Link} to="/quiz">Quiz</Button>
           <Button color="inherit" component={Link} to="/code-assistant">Assistant de Code</Button>
           <Button color="inherit" component={Link} to="/brainstorm">Remue-méninges</Button>
           <Button color="inherit" component={Link} to="/discord-bot">Bot Discord</Button>
         </Toolbar>
       </AppBar>
     );
   }

   export default Navbar;