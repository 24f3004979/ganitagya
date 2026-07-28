import express from 'express';
import mongoose from 'mongoose';
import dotenv from 'dotenv';
import cors from 'cors';

// Load environment configurations
dotenv.config();

const app = express();

// Global Middleware
app.use(cors({ origin: process.env.CLIENT_URL || 'http://localhost:5173' })); 
app.use(express.json()); // Parses incoming JSON payloads safely

// Test Route
app.get('/api/health', (req, res) => {
  res.status(200).json({ status: 'healthy', message: 'Server is running smoothly' });
});

// Database Connection & Server Startup
const PORT = process.env.PORT || 5000;

mongoose
  .connect(process.env.MONGO_URI)
  .then(() => {
    console.log('✅ Securely connected to MongoDB Cloud');
    app.listen(PORT, () => console.log(`🚀 Server burning fuel on port ${PORT}`));
  })
  .catch((err) => {
    console.error('❌ Database connection failure:', err.message);
    process.exit(1); // Shuts down app safely if database fails
  });

