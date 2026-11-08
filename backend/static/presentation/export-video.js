// Export video script for Ariary Numeric Presentation
// Usage: node export-video.js
// Requires: playwright (or puppeteer) and ffmpeg

const { chromium } = require('playwright');
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const CONFIG = {
  url: 'http://localhost:8080',
  width: 1920,
  height: 1080,
  fps: 30,
  outputDir: './export-frames',
  outputFile: 'ariary-numeric-presentation.mp4',
  sceneDuration: 0, // auto-detect from timeline
};

async function exportVideo() {
  console.log('🎬 Starting video export...');
  
  // Check dependencies
  try {
    execSync('ffmpeg -version', { stdio: 'ignore' });
  } catch (e) {
    console.error('❌ FFmpeg not found. Install with: sudo apt install ffmpeg');
    process.exit(1);
  }

  // Create output directory
  if (!fs.existsSync(CONFIG.outputDir)) {
    fs.mkdirSync(CONFIG.outputDir, { recursive: true });
  }

  // Launch browser
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  await page.setViewportSize({ width: CONFIG.width, height: CONFIG.height });

  console.log('🌐 Loading presentation...');
  await page.goto(CONFIG.url);
  await page.waitForTimeout(2000);

  // Start playback
  const playBtn = await page.$('#play-btn');
  if (playBtn) await playBtn.click();

  // Capture frames
  console.log('📸 Capturing frames...');
  let frameCount = 0;
  const captureInterval = 1000 / CONFIG.fps;
  
  // Get total duration from page
  const totalDuration = await page.evaluate(() => (window.TIMELINE || []).reduce((s, sc) => s + sc.duration, 0));
  const totalFrames = Math.ceil(totalDuration / captureInterval);
  
  console.log(`📊 Total duration: ${totalDuration}ms, ${totalFrames} frames at ${CONFIG.fps}fps`);

  for (let i = 0; i < totalFrames; i++) {
    const framePath = path.join(CONFIG.outputDir, `frame_${String(i).padStart(6, '0')}.png`);
    await page.screenshot({ path: framePath });
    frameCount++;
    
    if (i % 30 === 0) {
      console.log(`  Frame ${i}/${totalFrames} (${Math.round(i/totalFrames*100)}%)`);
    }
    
    await page.waitForTimeout(captureInterval);
  }

  await browser.close();
  console.log(`✅ Captured ${frameCount} frames`);

  // Assemble with FFmpeg
  console.log('🎞️ Assembling video with FFmpeg...');
  const ffmpegCmd = `ffmpeg -y -framerate ${CONFIG.fps} -i ${CONFIG.outputDir}/frame_%06d.png -c:v libx264 -pix_fmt yuv420p -crf 23 ${CONFIG.outputFile}`;
  execSync(ffmpegCmd, { stdio: 'inherit' });

  console.log(`✅ Video exported: ${CONFIG.outputFile}`);
}

exportVideo().catch(err => {
  console.error('❌ Export failed:', err);
  process.exit(1);
});