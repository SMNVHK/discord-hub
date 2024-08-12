import React from 'react';
import { Container, Typography, Card, CardContent, CardActions, Button, Grid } from '@mui/material';

function Quests() {
  const quests = [
    { id: 1, title: "AI Basics", description: "Learn the fundamentals of AI" },
    { id: 2, title: "Machine Learning 101", description: "Dive into machine learning algorithms" },
    { id: 3, title: "Neural Networks", description: "Explore the world of neural networks" },
  ];

  return (
    <Container>
      <Typography variant="h2" gutterBottom>
        AI Quests
      </Typography>
      <Grid container spacing={3}>
        {quests.map((quest) => (
          <Grid item xs={12} sm={6} md={4} key={quest.id}>
            <Card>
              <CardContent>
                <Typography variant="h5" component="div">
                  {quest.title}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {quest.description}
                </Typography>
              </CardContent>
              <CardActions>
                <Button size="small">Start Quest</Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Container>
  );
}

export default Quests;
