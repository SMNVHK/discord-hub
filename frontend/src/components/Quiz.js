import React, { useState, useEffect } from 'react';
   import { Button, Typography, RadioGroup, FormControlLabel, Radio } from '@mui/material';
   import { db } from '../services/firebase';
   import { ref, onValue } from "firebase/database";

   function Quiz() {
     const [currentQuestion, setCurrentQuestion] = useState(0);
     const [questions, setQuestions] = useState([]);
     const [score, setScore] = useState(0);
     const [showScore, setShowScore] = useState(false);
     const [answer, setAnswer] = useState('');

     useEffect(() => {
       const questionsRef = ref(db, 'quiz/questions');
       onValue(questionsRef, (snapshot) => {
         const data = snapshot.val();
         setQuestions(data);
       });
     }, []);

     const handleAnswerSubmit = () => {
       if (answer === questions[currentQuestion].correctAnswer) {
         setScore(score + 1);
       }

       const nextQuestion = currentQuestion + 1;
       if (nextQuestion < questions.length) {
         setCurrentQuestion(nextQuestion);
         setAnswer('');
       } else {
         setShowScore(true);
       }
     };

     if (questions.length === 0) return <Typography>Chargement des questions...</Typography>;

     if (showScore) {
       return <Typography>Vous avez obtenu {score} sur {questions.length}!</Typography>;
     }

     return (
       <div>
         <Typography variant="h4">Question {currentQuestion + 1}</Typography>
         <Typography>{questions[currentQuestion].question}</Typography>
         <RadioGroup value={answer} onChange={(e) => setAnswer(e.target.value)}>
           {questions[currentQuestion].options.map((option, index) => (
             <FormControlLabel key={index} value={option} control={<Radio />} label={option} />
           ))}
         </RadioGroup>
         <Button onClick={handleAnswerSubmit}>Soumettre</Button>
       </div>
     );
   }

   export default Quiz;
