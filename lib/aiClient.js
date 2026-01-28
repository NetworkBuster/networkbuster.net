/* Simple AI client wrapper for recycling recommendations.
 * Uses OPENAI_API_KEY if present; otherwise falls back to rule-based heuristics.
 * Exports: getRecommendations(items, context, prefs)
 */
import fs from 'fs';

const OPENAI_KEY = process.env.OPENAI_API_KEY || process.env.OPENAI_API;

async function callOpenAI(prompt) {
  if (!OPENAI_KEY) throw new Error('OpenAI key not configured');
  const res = await fetch('https://api.openai.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${OPENAI_KEY}`
    },
    body: JSON.stringify({
      model: 'gpt-4o-mini',
      messages: [{ role: 'system', content: 'You are an assistant that provides recycling guidance.' }, { role: 'user', content: prompt }],
      max_tokens: 500
    })
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`OpenAI error: ${res.status} ${body}`);
  }
  const data = await res.json();
  const txt = data?.choices?.[0]?.message?.content || '';
  return txt;
}

function heuristicRecommendations(items = []) {
  const recs = [];
  for (const it of items) {
    const name = (it.name || '').toLowerCase();
    if (name.includes('cardboard') || name.includes('box')) {
      recs.push({ action: 'recycle', reason: 'Cardboard and paperboard are often accepted in curbside recycling. Remove liquids and grease.', confidence: 0.9 });
    } else if (name.includes('pizza') || name.includes('greasy')) {
      recs.push({ action: 'compost', reason: 'Greasy cardboard is better composted or thrown away if contaminated.', confidence: 0.8 });
    } else if (name.includes('bottle') || name.includes('plastic bottle')) {
      recs.push({ action: 'recycle', reason: 'Rinse and place in curbside recycling if accepted locally.', confidence: 0.95 });
    } else if (name.includes('glass')) {
      recs.push({ action: 'recycle', reason: 'Glass is recyclable in many curbside programs; check local rules.', confidence: 0.9 });
    } else {
      recs.push({ action: 'unknown', reason: 'No heuristic; consider checking local disposal guidelines.', confidence: 0.5 });
    }
  }
  return recs;
}

export async function getRecommendations(items = [], context = {}, prefs = {}) {
  // Build prompt
  const inputSummary = (items || []).map(i => `${i.name}${i.context ? ' (' + i.context + ')' : ''}`).join(', ');
  const prompt = `User items: ${inputSummary}\nContext: ${JSON.stringify(context)}\nPreferences: ${JSON.stringify(prefs)}\nGive per-item recommendation with short reason and confidence as JSON array [{item, action, reason, confidence}]`;

  if (OPENAI_KEY) {
    try {
      const txt = await callOpenAI(prompt);
      // Try to extract JSON from the model output
      const m = txt.match(/\[\s*\{/s);
      if (m) {
        const jsonStart = m.index;
        const j = txt.slice(jsonStart);
        try {
          const parsed = JSON.parse(j);
          return { source: 'llm', raw: txt, recommendations: parsed };
        } catch (err) {
          // Fall back to heuristics
          return { source: 'llm-failed', raw: txt, recommendations: heuristicRecommendations(items) };
        }
      }
      return { source: 'llm-text', raw: txt, recommendations: heuristicRecommendations(items) };
    } catch (err) {
      console.warn('LLM call failed, using heuristics', err.message);
      return { source: 'fallback', recommendations: heuristicRecommendations(items) };
    }
  }

  // No key: return heuristics
  return { source: 'heuristic', recommendations: heuristicRecommendations(items) };
}

export default { getRecommendations };
