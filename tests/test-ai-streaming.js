import { chat } from '../lib/aiProviders.js';

async function testStreaming() {
    console.log('Testing AI Streaming (Rapid Answers)...');

    try {
        const stream = await chat('openai', [
            { role: 'user', content: 'Tell me a short story about a fast robot in 50 words.' }
        ], {
            stream: true,
            model: 'gpt-4o-mini'
        });

        if (!(stream instanceof ReadableStream)) {
            console.error('Error: Did not receive a ReadableStream');
            return;
        }

        const reader = stream.getReader();
        const decoder = new TextDecoder();
        let fullContent = '';

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value, { stream: true });
            // OpenAI streaming format is Data: { ... }
            const lines = chunk.split('\n').filter(line => line.trim() !== '');

            for (const line of lines) {
                if (line === 'data: [DONE]') continue;
                if (line.startsWith('data: ')) {
                    try {
                        const data = JSON.parse(line.substring(6));
                        const content = data.choices?.[0]?.delta?.content || '';
                        process.stdout.write(content);
                        fullContent += content;
                    } catch (e) {
                        // Ignore incomplete JSON chunks
                    }
                }
            }
        }

        console.log('\n\n✅ Streaming complete!');
    } catch (err) {
        console.error('Streaming test failed:', err.message);
    }
}

testStreaming();
