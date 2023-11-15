const WebSocket = require('ws');
const fs = require('fs');
const crypto = require('crypto');

const timePerChunk = 0.1; // seconds
const numChannel = 1;
const numQuantify = 16;
const sampleRate = 16000;
const bytesPerChunk = Math.floor(sampleRate * numQuantify * timePerChunk * numChannel / 8);

const apiUrl = 'wss://asr-dev.abcpen.com';

function generateSignature(appId, apiKey) {
    const ts = Math.floor(Date.now() / 1000).toString();
    const tt = Buffer.from(appId + ts, 'utf-8');
    const md5 = crypto.createHash('md5');
    md5.update(tt);
    const baseString = md5.digest('hex');
    const apiKeyBuffer = Buffer.from(apiKey, 'utf-8');
    const hmacSha1 = crypto.createHmac('sha1', apiKeyBuffer);
    hmacSha1.update(Buffer.from(baseString, 'utf-8'));
    const signa = hmacSha1.digest('base64');
    return { signa, ts };
}

async function sendAudioData(websocket) {
    const filename = '../dataset/3-1.wav';
    const fileData = fs.readFileSync(filename);
    const waveFileSampleRate = 16000; // Assuming a constant sample rate
    const numSamples = fileData.length / 2; // Assuming 16-bit samples
    const chunkSize = Math.floor(timePerChunk * waveFileSampleRate * 2);

    let start = 0;
    while (start < numSamples * 2) {
        const end = Math.min(start + chunkSize, numSamples * 2);
        const chunk = fileData.slice(start, end);
        await websocket.send(chunk);
        start = end;
        await new Promise(resolve => setTimeout(resolve, 30)); // Sleep for 30 milliseconds
    }
}

async function receiveRecognitionResult(websocket) {
    let segSentence = 0;

    function waitForMessage() {
        return new Promise((resolve, reject) => {
            websocket.once('message', (result) => resolve(result));
            websocket.once('close', () => reject(new Error('Connection closed')));
            websocket.once('error', (err) => reject(err));
        });
    }

    try {
        while (true) {
            const result = await waitForMessage();
            const asrText = JSON.parse(result);
            const asr = asrText.asr;
            const asrPunc = asrText.asr_punc || '';
            const segId = asrText.seg_id;
            const isFinal = asrText.is_final;
            const translate = asrText.translate || '';

            if (isFinal) {
                console.log(`${segSentence}:${asrPunc} -> ${translate}`);
                segSentence++;
            } else {
                process.stdout.write(`${segSentence}:${asr} -> ${translate}`);
            }
        }
    } catch (err) {
        console.error(`receiveRecognitionResult error: ${err}`);
    }
}


async function connectToServer() {
    const appId = 'test1';
    const appSecret = '2258ACC4-199B-4DCB-B6F3-C2485C63E85A';

    const { signa, ts } = generateSignature(appId, appSecret);

    const base_url = `${apiUrl}/v2/asr/ws`;
    const urlAsrApply = `${base_url}?appid=${appId}&ts=${ts}&signa=${encodeURIComponent(signa)}&asr_type=2&trans_mode=1&target_lang=ru&pd=court`;

    const websocket = new WebSocket(urlAsrApply);

    websocket.on('open', async () => {
        try {
            await sendAudioData(websocket);
        } catch (err) {
            console.error(`sendAudioData error: ${err}`);
        }
    });

    websocket.on('close', () => {
        console.log('Connection closed');
    });

    websocket.on('error', (err) => {
        console.error(`WebSocket error: ${err}`);
    });

    await receiveRecognitionResult(websocket);
}

try {
    connectToServer();
} catch (err) {
    console.error(`connectToServer error: ${err}`);
}
