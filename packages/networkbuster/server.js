const express = require('express');
const app = express();
const PORT = process.env.NETWORKBUSTER_PORT || 4000;

app.use(express.json());

app.get('/', (req, res) => {
  res.send('<h1>NetworkBuster App</h1><p>Welcome, pilots.</p>');
});

app.get('/info', (req, res) => {
  res.json({ ok: true, service: 'networkbuster', port: PORT });
});

app.listen(PORT, () => console.log(`networkbuster app listening on ${PORT}`));
module.exports = app;