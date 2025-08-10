/**
 * @file tone-processor.js - AudioWorklet for real-time pitch detection.
 */
class Yin {
    constructor(sampleRate, threshold) {
        this.sampleRate = sampleRate;
        this.threshold = threshold;
        this.bufferSize = 1024;
        this.yinBuffer = new Float32Array(this.bufferSize / 2);
    }
    getPitch(data) {
        let tauEstimate = -1;
        for (let tau = 0; tau < this.yinBuffer.length; tau++) {
            this.yinBuffer[tau] = 0;
            for (let i = 0; i < this.yinBuffer.length; i++) {
                const delta = data[i] - data[i + tau];
                this.yinBuffer[tau] += delta * delta;
            }
        }
        let runningSum = 0;
        this.yinBuffer[0] = 1;
        for (let tau = 1; tau < this.yinBuffer.length; tau++) {
            runningSum += this.yinBuffer[tau];
            this.yinBuffer[tau] *= tau / runningSum;
        }
        for (let tau = 1; tau < this.yinBuffer.length; tau++) {
            if (this.yinBuffer[tau] < this.threshold) {
                tauEstimate = tau;
                while (tau + 1 < this.yinBuffer.length && this.yinBuffer[tau + 1] < this.yinBuffer[tau]) {
                    tauEstimate = ++tau;
                }
                break;
            }
        }
        let betterTau, clarity = 0;
        if (tauEstimate !== -1) {
            const x0 = (tauEstimate < 1) ? tauEstimate : tauEstimate - 1;
            const x2 = (tauEstimate + 1 < this.yinBuffer.length) ? tauEstimate + 1 : tauEstimate;
            const s0 = this.yinBuffer[x0], s1 = this.yinBuffer[tauEstimate], s2 = this.yinBuffer[x2];
            betterTau = tauEstimate + (s2 - s0) / (2 * (2 * s1 - s2 - s0));
            clarity = 1 - this.yinBuffer[tauEstimate];
        }
        if (tauEstimate === -1 || !betterTau) return { pitch: -1, clarity: 0 };
        return { pitch: this.sampleRate / betterTau, clarity };
    }
}

class ToneProcessor extends AudioWorkletProcessor {
    constructor() {
        super();
        this.yin = new Yin(sampleRate, 0.15); // `sampleRate` is a global in AudioWorklets
    }
    process(inputs) {
        const channel = inputs[0][0];
        if (!channel) return true;
        let rms = Math.sqrt(channel.reduce((sum, val) => sum + val * val, 0) / channel.length);
        if (rms > 0.01) { // Process only if signal is loud enough
            const { pitch, clarity } = this.yin.getPitch(channel);
            this.port.postMessage({ pitch, clarity });
        } else {
            this.port.postMessage({ pitch: -1, clarity: 0 });
        }
        return true;
    }
}
registerProcessor('tone-processor', ToneProcessor);