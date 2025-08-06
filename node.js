// A simple Node.js server using Express to simulate a song API.

// Import the Express library.
const express = require('express');
const cors = require('cors');
const app = express();
const port = 3000; // The server will run on this port.

// Enable CORS to allow the frontend app to access this server.
app.use(cors());

// Define a hardcoded song data object.
const songData = {
  id: 'song-123',
  title: 'Sample Song',
  artist: 'Example Artist',
  albumArt: 'https://placehold.co/100x100/1DB954/white?text=Sample',
  // IMPORTANT: This is a sample URL to a public domain audio file.
  // In a real app, this would be a link to your actual audio file.
  audioUrl: 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3',
};

// Define an API endpoint to get song data by ID.
// When the frontend makes a GET request to http://localhost:3000/api/songs/song-123,
// this function will run.
app.get('/api/songs/:id', (req, res) => {
  console.log(`Received request for song ID: ${req.params.id}`);

  // For this example, we'll just return the same song data regardless of the ID.
  // In a real application, you would fetch the song from a database.
  if (req.params.id === 'song-123') {
    res.json(songData);
  } else {
    res.status(404).json({ error: 'Song not found' });
  }
});

// Start the server.
app.listen(port, () => {
  console.log(`Legeztify backend server listening at http://localhost:${port}`);
});

// To run this server:
// 1. Make sure you have Node.js installed.
// 2. Create a new directory for your server.
// 3. Save this code as 'server.js'.
// 4. In your terminal, navigate to that directory.
// 5. Run 'npm init -y' to create a package.json file.
// 6. Run 'npm install express cors' to install the required libraries.
// 7. Run 'node server.js' to start the server.
// 8. You should see a message in your terminal indicating the server is running.
