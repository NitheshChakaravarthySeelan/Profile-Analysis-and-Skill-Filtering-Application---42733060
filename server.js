
const express = require('express');
const mongoose = require('mongoose');
const app = express();

app.use(express.json());

mongoose.connect('mongodb://localhost:27017/profiles', {
  useNewUrlParser: true,
  useUnifiedTopology: true,
});

const profileSchema = new mongoose.Schema({
  name: String,
  skills: [String],
});

const Profile = mongoose.model('Profile', profileSchema);
app.post('/profiles', async (req, res) => {
  const { name, skills } = req.body;
  const profile = new Profile({ name, skills });
  await profile.save();
  res.status(201).send('Profile created');
});

app.get('/profiles/filter', async (req, res) => {
  const { skill } = req.query;
  const profiles = await Profile.find({ skills: skill });
  res.json(profiles);
});
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
