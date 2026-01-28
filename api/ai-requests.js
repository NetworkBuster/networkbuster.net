/**
 * AI Requests API - Express router for device AI inference requests
 * Provides endpoints for chat, embeddings, and image generation
 * Integrates with device registration for authentication
 */

import express from 'express';
import crypto from 'crypto';
import { getRegistration } from '../lib/deviceStore.js';
import aiProviders from '../lib/aiProviders.js';

const router = express.Router();

// Device authentication middleware
function authenticateDevice(req, res, next) {
    // Check for device ID in header or query
    const deviceId = req.headers['x-device-id'] || req.query.deviceId;
    const apiKey = req.headers['x-api-key'] || req.headers['authorization']?.replace('Bearer ', '');

    // Allow API key authentication (for testing or non-registered devices)
    if (apiKey && apiKey === process.env.AI_API_KEY) {
        req.deviceId = 'api-key-user';
        req.authenticated = true;
        return next();
    }

    // Device ID authentication
    if (deviceId) {
        const device = getRegistration(deviceId);
        if (device) {
            req.deviceId = deviceId;
            req.device = device;
            req.authenticated = true;
            return next();
        }
    }

    // Allow anonymous requests if configured
    if (process.env.AI_ALLOW_ANONYMOUS === 'true') {
        req.deviceId = 'anonymous-' + crypto.randomBytes(4).toString('hex');
        req.authenticated = false;
        return next();
    }

    return res.status(401).json({
        error: 'Authentication required',
        message: 'Provide X-Device-Id header with registered device ID or X-API-Key header'
    });
}

// Rate limit info middleware
function addRateLimitHeaders(req, res, next) {
    const rateInfo = aiProviders.checkRateLimit(req.deviceId);
    res.setHeader('X-RateLimit-Remaining', rateInfo.remaining);
    res.setHeader('X-RateLimit-Reset', rateInfo.resetIn);
    next();
}

// GET /api/ai/providers - List available AI providers
router.get('/providers', (req, res) => {
    const providers = aiProviders.getAvailableProviders();
    const defaultProvider = aiProviders.getDefaultProvider();

    res.json({
        providers,
        default: defaultProvider,
        timestamp: new Date().toISOString()
    });
});

// POST /api/ai/chat - Chat completion
router.post('/chat', authenticateDevice, addRateLimitHeaders, async (req, res) => {
    try {
        const {
            provider = aiProviders.getDefaultProvider(),
            messages,
            model,
            maxTokens,
            temperature,
            useCache = true
        } = req.body;

        if (!messages || !Array.isArray(messages) || messages.length === 0) {
            return res.status(400).json({ error: 'messages array is required' });
        }

        if (!provider) {
            return res.status(503).json({ error: 'No AI providers configured' });
        }

        if (!aiProviders.isProviderAvailable(provider)) {
            return res.status(400).json({ error: `Provider '${provider}' is not available` });
        }

        const result = await aiProviders.chat(provider, messages, {
            model,
            maxTokens,
            temperature,
            deviceId: req.deviceId,
            useCache
        });

        // Track usage
        const tokens = (result.usage?.total_tokens || result.usage?.input_tokens + result.usage?.output_tokens) || 0;
        aiProviders.trackUsage(req.deviceId, provider, 'chat', tokens);

        res.json({
            success: true,
            ...result,
            deviceId: req.deviceId,
            timestamp: new Date().toISOString()
        });

    } catch (err) {
        console.error('AI Chat error:', err.message);

        if (err.message.includes('Rate limit exceeded')) {
            return res.status(429).json({ error: err.message });
        }

        res.status(500).json({
            error: 'AI request failed',
            message: err.message
        });
    }
});

// POST /api/ai/embed - Generate embeddings
router.post('/embed', authenticateDevice, addRateLimitHeaders, async (req, res) => {
    try {
        const {
            provider = aiProviders.getDefaultProvider(),
            text,
            model
        } = req.body;

        if (!text) {
            return res.status(400).json({ error: 'text is required (string or array of strings)' });
        }

        if (!provider) {
            return res.status(503).json({ error: 'No AI providers configured' });
        }

        if (!aiProviders.isProviderAvailable(provider)) {
            return res.status(400).json({ error: `Provider '${provider}' is not available` });
        }

        const result = await aiProviders.embed(provider, text, {
            model,
            deviceId: req.deviceId
        });

        aiProviders.trackUsage(req.deviceId, provider, 'embed', result.usage?.total_tokens || 0);

        res.json({
            success: true,
            ...result,
            deviceId: req.deviceId,
            timestamp: new Date().toISOString()
        });

    } catch (err) {
        console.error('AI Embed error:', err.message);

        if (err.message.includes('Rate limit exceeded')) {
            return res.status(429).json({ error: err.message });
        }

        if (err.message.includes('does not support embeddings')) {
            return res.status(400).json({ error: err.message });
        }

        res.status(500).json({
            error: 'Embedding request failed',
            message: err.message
        });
    }
});

// POST /api/ai/image - Generate images
router.post('/image', authenticateDevice, addRateLimitHeaders, async (req, res) => {
    try {
        const {
            provider = 'openai', // Only OpenAI supports images for now
            prompt,
            model,
            size,
            quality,
            n
        } = req.body;

        if (!prompt) {
            return res.status(400).json({ error: 'prompt is required' });
        }

        if (!aiProviders.isProviderAvailable(provider)) {
            return res.status(400).json({ error: `Provider '${provider}' is not available` });
        }

        const result = await aiProviders.generateImage(provider, prompt, {
            model,
            size,
            quality,
            n,
            deviceId: req.deviceId
        });

        aiProviders.trackUsage(req.deviceId, provider, 'image', 0);

        res.json({
            success: true,
            ...result,
            deviceId: req.deviceId,
            timestamp: new Date().toISOString()
        });

    } catch (err) {
        console.error('AI Image error:', err.message);

        if (err.message.includes('Rate limit exceeded')) {
            return res.status(429).json({ error: err.message });
        }

        if (err.message.includes('does not support image')) {
            return res.status(400).json({ error: err.message });
        }

        res.status(500).json({
            error: 'Image generation failed',
            message: err.message
        });
    }
});

// GET /api/ai/usage - Get device usage statistics
router.get('/usage', authenticateDevice, (req, res) => {
    const usage = aiProviders.getDeviceUsage(req.deviceId);
    const rateInfo = aiProviders.checkRateLimit(req.deviceId);

    res.json({
        deviceId: req.deviceId,
        usage,
        rateLimit: {
            remaining: rateInfo.remaining,
            resetIn: rateInfo.resetIn,
            limit: parseInt(process.env.AI_RATE_LIMIT_PER_MINUTE || '60')
        },
        timestamp: new Date().toISOString()
    });
});

// GET /api/ai/usage/all - Get all usage (admin only)
router.get('/usage/all', authenticateDevice, (req, res) => {
    const apiKey = req.headers['x-api-key'] || req.headers['authorization']?.replace('Bearer ', '');

    if (apiKey !== process.env.AI_API_KEY && apiKey !== process.env.ADMIN_KEY) {
        return res.status(403).json({ error: 'Admin access required' });
    }

    const allUsage = aiProviders.getAllUsage();

    res.json({
        usage: allUsage,
        totalDevices: Object.keys(allUsage).length,
        timestamp: new Date().toISOString()
    });
});

// Health check
router.get('/health', (req, res) => {
    const providers = aiProviders.getAvailableProviders();

    res.json({
        status: 'ok',
        providersAvailable: providers.length,
        defaultProvider: aiProviders.getDefaultProvider(),
        timestamp: new Date().toISOString()
    });
});

export default router;
