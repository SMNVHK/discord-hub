import React from 'react';
import { Container, Typography, Card, CardContent, CardActions, Button, Grid } from '@mui/material';

function AILab() {
  const experiments = [
    { id: 1, title: "Image Classification", description: "Classify images using a pre-trained model" },
    { id: 2, title: "Text Generation", description: "Generate text using a language model" },
    { id: 3, title: "Sentiment Analysis", description: "Analyze the sentiment of text input" },
  ];

  return (
    <Container>
      <Typography variant="h2" gutterBottom>
        AI Lab
      </Typography>
      <Typography variant="body1" paragraph>
        Welcome to the AI Lab! Here you can experiment with various AI models and see them in action.
      </Typography>
      <Grid container spacing={3}>
        {experiments.map((exp) => (
          <Grid item xs={12} sm={6} md={4} key={exp.id}>
            <Card>
              <CardContent>
                <Typography variant="h5" component="div">
                  {exp.title}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {exp.description}
                </Typography>
              </CardContent>
              <CardActions>
                <Button size="small">Try Experiment</Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Container>
  );
}

export default AILab;