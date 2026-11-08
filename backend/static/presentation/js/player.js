// Main player for Ariary Numeric Presentation
class PresentationPlayer {
  constructor() {
    this.currentScene = 0;
    this.isPlaying = false;
    this.isPaused = false;
    this.currentTime = 0;
    this.totalTime = TOTAL_DURATION;
    this.cursor = null;
    this.subtitleManager = null;
    this.audioManager = null;
    this.scenes = [];
    this.sceneElements = [];
    this.transitionOverlay = null;
    this.animationFrame = null;
    this.lastTimestamp = 0;
  }

  init() {
    this.cursor = new CursorAnimator(document.getElementById('cursor'));
    this.subtitleManager = new SubtitleManager(document.getElementById('subtitle-container'));
    this.audioManager = new AudioManager();
    this.audioManager.init();

    // Collect scenes
    this.scenes = document.querySelectorAll('.scene');
    this.sceneElements = Array.from(this.scenes);

    // Transition overlay
    this.transitionOverlay = document.getElementById('scene-transition');

    // Setup controls
    this.setupControls();

    // Start at scene 0
    this.showScene(0);
  }

  setupControls() {
    const playBtn = document.getElementById('play-btn');
    const pauseBtn = document.getElementById('pause-btn');
    const restartBtn = document.getElementById('restart-btn');
    const muteBtn = document.getElementById('mute-btn');
    const subtitleBtn = document.getElementById('subtitle-btn');
    const fullscreenBtn = document.getElementById('fullscreen-btn');
    const voiceSlider = document.getElementById('voice-volume');
    const musicSlider = document.getElementById('music-volume');

    if (playBtn) playBtn.addEventListener('click', () => this.play());
    if (pauseBtn) pauseBtn.addEventListener('click', () => this.pause());
    if (restartBtn) restartBtn.addEventListener('click', () => this.restart());
    if (muteBtn) muteBtn.addEventListener('click', () => this.toggleMute());
    if (subtitleBtn) subtitleBtn.addEventListener('click', () => this.toggleSubtitles());
    if (fullscreenBtn) fullscreenBtn.addEventListener('click', () => this.toggleFullscreen());
    if (voiceSlider) voiceSlider.addEventListener('input', (e) => this.audioManager.setVoiceVolume(e.target.value / 100));
    if (musicSlider) musicSlider.addEventListener('input', (e) => this.audioManager.setMusicVolume(e.target.value / 100));
  }

  play() {
    if (this.isPaused) {
      this.isPaused = false;
    } else {
      this.currentTime = 0;
      this.showScene(0);
    }
    this.isPlaying = true;
    this.lastTimestamp = performance.now();
    this.animate();
    this.updatePlayPauseButtons();
  }

  pause() {
    this.isPaused = true;
    this.isPlaying = false;
    if (this.animationFrame) {
      cancelAnimationFrame(this.animationFrame);
      this.animationFrame = null;
    }
    if (this.audioManager) this.audioManager.stopNarration();
    this.updatePlayPauseButtons();
  }

  restart() {
    this.pause();
    this.currentTime = 0;
    this.showScene(0);
    this.updateProgress();
    setTimeout(() => this.play(), 500);
  }

  toggleMute() {
    this.audioManager.muted = !this.audioManager.muted;
    this.audioManager.setMuted(this.audioManager.muted);
    const muteBtn = document.getElementById('mute-btn');
    if (muteBtn) muteBtn.textContent = this.audioManager.muted ? '🔇' : '🔊';
  }

  toggleSubtitles() {
    const container = document.getElementById('subtitle-container');
    if (container) {
      container.style.display = container.style.display === 'none' ? 'block' : 'none';
    }
  }

  toggleFullscreen() {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen().catch(() => {});
    } else {
      document.exitFullscreen();
    }
  }

  animate() {
    if (!this.isPlaying || this.isPaused) return;

    const now = performance.now();
    const delta = now - this.lastTimestamp;
    this.lastTimestamp = now;
    this.currentTime += delta;

    if (this.currentTime >= this.totalTime) {
      this.currentTime = this.totalTime;
      this.pause();
      this.updateProgress();
      return;
    }

    // Update scene
    const { scene, index, localTime } = getSceneAtTime(this.currentTime);
    if (index !== this.currentScene) {
      this.transitionToScene(index);
    }

    // Update cursor
    this.updateCursor(scene, localTime);

    // Update subtitle
    this.updateSubtitle(scene, localTime);

    // Update progress bar
    this.updateProgress();

    this.animationFrame = requestAnimationFrame(() => this.animate());
  }

  showScene(index) {
    this.scenes.forEach((scene, i) => {
      scene.classList.toggle('active', i === index);
    });
    this.currentScene = index;
  }

  transitionToScene(index) {
    if (this.transitionOverlay) {
      this.transitionOverlay.classList.add('active');
      setTimeout(() => {
        this.showScene(index);
        setTimeout(() => {
          this.transitionOverlay.classList.remove('active');
        }, 100);
      }, 300);
    } else {
      this.showScene(index);
    }
  }

  updateCursor(scene, localTime) {
    if (!scene.cursor || !this.cursor) {
      this.cursor.hide();
      return;
    }

    this.cursor.show();
    const { start, end, clickAt, typing } = scene.cursor;
    const sceneDuration = scene.duration;
    const progress = localTime / sceneDuration;

    // Move cursor from start to end
    const x = start.x + (end.x - start.x) * progress;
    const y = start.y + (end.y - start.y) * progress;
    this.cursor.x = x;
    this.cursor.y = y;
    this.cursor.updatePosition();

    // Click at specified time
    if (clickAt && Math.abs(localTime - clickAt) < 50) {
      this.cursor.click();
    }

    // Typing effect
    if (typing && localTime > clickAt && localTime < clickAt + 3000) {
      // Simulate typing
    }
  }

  updateSubtitle(scene, localTime) {
    if (!this.subtitleManager) return;

    if (localTime < 500 && scene.subtitle) {
      this.subtitleManager.show(scene.subtitle, scene.duration - 500);
    }
  }

  updateProgress() {
    const progress = getProgress(this.currentTime);
    const progressBar = document.getElementById('progress-bar');
    const timeDisplay = document.getElementById('time-display');

    if (progressBar) {
      progressBar.style.width = (progress * 100) + '%';
    }

    if (timeDisplay) {
      const current = this.formatTime(this.currentTime);
      const total = this.formatTime(this.totalTime);
      timeDisplay.textContent = `${current} / ${total}`;
    }
  }

  formatTime(ms) {
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  }

  updatePlayPauseButtons() {
    const playBtn = document.getElementById('play-btn');
    const pauseBtn = document.getElementById('pause-btn');
    if (playBtn) playBtn.style.display = this.isPlaying ? 'none' : 'inline-flex';
    if (pauseBtn) pauseBtn.style.display = this.isPlaying ? 'inline-flex' : 'none';
  }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  const player = new PresentationPlayer();
  player.init();
  window.player = player;
});