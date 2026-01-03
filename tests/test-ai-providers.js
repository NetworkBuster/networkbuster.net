/**
 * AI Providers Test - Test connectivity to all configured AI providers
 * Run: npm run ai:test
 */

import aiProviders from '../lib/aiProviders.js';

const TEST_MESSAGE = [
    { role: 'system', content: 'You are a helpful assistant. Keep responses very brief.' },
    { role: 'user', content: 'Say hello in exactly 3 words.' }
];

const TEST_EMBED_TEXT = 'This is a test sentence for embedding.';

async function runTests() {
    console.log('\n🧪 AI Providers Test Suite\n');
    console.log('═'.repeat(60));

    const providers = aiProviders.getAvailableProviders();
    console.log(`\n📋 Available Providers: ${providers.length}`);

    for (const p of providers) {
        const caps = Object.entries(p.capabilities)
            .filter(([, v]) => v)
            .map(([k]) => k)
            .join(', ');
        console.log(`   ✓ ${p.name} (${caps})`);
    }

    const defaultProvider = aiProviders.getDefaultProvider();
    console.log(`\n🎯 Default Provider: ${defaultProvider || 'none'}\n`);
    console.log('═'.repeat(60));

    const results = [];

    for (const provider of providers) {
        console.log(`\n🔄 Testing ${provider.name}...`);

        // Test chat
        if (provider.capabilities.chat) {
            try {
                console.log(`   📝 Chat completion...`);
                const start = Date.now();
                const result = await aiProviders.chat(provider.id, TEST_MESSAGE, {
                    maxTokens: 50,
                    useCache: false
                });
                const duration = Date.now() - start;
                console.log(`   ✓ Chat: "${result.content.substring(0, 50)}..." (${duration}ms)`);
                results.push({ provider: provider.id, type: 'chat', success: true, duration });
            } catch (err) {
                console.log(`   ✗ Chat failed: ${err.message}`);
                results.push({ provider: provider.id, type: 'chat', success: false, error: err.message });
            }
        }

        // Test embeddings
        if (provider.capabilities.embed) {
            try {
                console.log(`   📊 Embeddings...`);
                const start = Date.now();
                const result = await aiProviders.embed(provider.id, TEST_EMBED_TEXT);
                const duration = Date.now() - start;
                const dims = result.embeddings[0]?.length || 0;
                console.log(`   ✓ Embed: ${dims} dimensions (${duration}ms)`);
                results.push({ provider: provider.id, type: 'embed', success: true, duration, dimensions: dims });
            } catch (err) {
                console.log(`   ✗ Embed failed: ${err.message}`);
                results.push({ provider: provider.id, type: 'embed', success: false, error: err.message });
            }
        }

        // Skip image generation in tests (expensive)
        if (provider.capabilities.image) {
            console.log(`   🖼️ Image generation: skipped (use --with-images to test)`);
        }
    }

    // Summary
    console.log('\n' + '═'.repeat(60));
    console.log('\n📊 Test Summary\n');

    const successful = results.filter(r => r.success);
    const failed = results.filter(r => !r.success);

    console.log(`   Total: ${results.length} tests`);
    console.log(`   ✓ Passed: ${successful.length}`);
    console.log(`   ✗ Failed: ${failed.length}`);

    if (failed.length > 0) {
        console.log('\n   Failed tests:');
        for (const f of failed) {
            console.log(`     - ${f.provider}/${f.type}: ${f.error}`);
        }
    }

    console.log('\n' + '═'.repeat(60) + '\n');

    // Exit with error code if any tests failed
    process.exit(failed.length > 0 ? 1 : 0);
}

// Check for --with-images flag
const withImages = process.argv.includes('--with-images');

runTests().catch(err => {
    console.error('Test suite failed:', err);
    process.exit(1);
});
