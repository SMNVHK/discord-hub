const requiredEnvVars = [
  'REACT_APP_FIREBASE_API_KEY',
  'REACT_APP_FIREBASE_AUTH_DOMAIN',
  'REACT_APP_FIREBASE_DATABASE_URL',
  'REACT_APP_FIREBASE_PROJECT_ID',
  'REACT_APP_FIREBASE_STORAGE_BUCKET',
  'REACT_APP_FIREBASE_MESSAGING_SENDER_ID',
  'REACT_APP_FIREBASE_APP_ID'
];

const missingVars = requiredEnvVars.filter(varName => !process.env[varName]);

if (missingVars.length > 0) {
  console.warn(`Attention : Les variables d'environnement suivantes ne sont pas définies : ${missingVars.join(', ')}`);
  console.log('Variables d\'environnement définies :');
  requiredEnvVars.forEach(varName => {
    console.log(`${varName}: ${process.env[varName] ? 'Définie' : 'Non définie'}`);
  });
} else {
  console.log('Toutes les variables d\'environnement requises sont définies.');
}

// Ne pas faire échouer le build, juste avertir
process.exit(0);