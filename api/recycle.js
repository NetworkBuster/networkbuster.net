import express from 'express';
import aiClient from '../lib/aiClient.js';
import profileStore from '../lib/profileStore.js';

const router = express.Router();

// POST /api/recycle/recommend
router.post('/recommend', async (req, res) => {
  const { userId, location, items = [], preferences = {} } = req.body || {};
  try {
    const profile = userId ? profileStore.getProfile(userId) : null;
    const prefs = Object.assign({}, profile?.preferences || {}, preferences);
    const context = { location, profile: profile ? { id: userId } : null };
    const out = await aiClient.getRecommendations(items, context, prefs);
    res.json({ ok: true, source: out.source, recommendations: out.recommendations, raw: out.raw || null });
  } catch (err) {
    console.error('Recommend error', err);
    res.status(500).json({ ok: false, error: err.message });
  }
});

// POST /api/recycle/feedback
router.post('/feedback', (req, res) => {
  const { userId, item, action, rating, notes } = req.body || {};
  try {
    const fb = { userId: userId || 'anon', item, action, rating, notes, ts: new Date().toISOString() };
    const filepath = profileStore.appendFeedback(fb);
    res.json({ ok: true, stored: filepath });
  } catch (err) {
    res.status(500).json({ ok: false, error: err.message });
  }
});

export default router;
