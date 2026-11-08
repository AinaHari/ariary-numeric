// Audio management system
class AudioManager {
  constructor() {
    this.narration = null;
    this.music = null;
    this.sfx = {};
    this.muted = false;
    this.volume = 1.0;
    this.musicVolume = 0.3;
    this.voiceVolume = 1.0;
    this.sfxVolume = 0.5;
  }

  init() {
    this.music = new Audio();
    this.music.loop = true;
    this.music.volume = this.musicVolume;
  }

  playNarration(src) {
    if (this.muted) return;
    if (this.narration) {
      this.narration.pause();
      this.narration = null;
    }
    if (src) {
      this.narration = new Audio(src);
      this.narration.volume = this.voiceVolume;
      this.narration.play().catch(() => {});
    }
  }

  stopNarration() {
    if (this.narration) {
      this.narration.pause();
      this.narration = null;
    }
  }

  playMusic(src) {
    if (this.muted || !this.music) return;
    if (src) {
      this.music.src = src;
      this.music.volume = this.musicVolume;
      this.music.play().catch(() => {});
    }
  }

  stopMusic() {
    if (this.music) {
      this.music.pause();
    }
  }

  playSfx(name) {
    if (this.muted) return;
    // Placeholder for sound effects
    // In production, load actual sound files
  }

  setMuted(muted) {
    this.muted = muted;
    if (this.narration) this.narration.volume = muted ? 0 : this.voiceVolume;
    if (this.music) this.music.volume = muted ? 0 : this.musicVolume;
  }

  setVoiceVolume(vol) {
    this.voiceVolume = vol;
    if (this.narration) this.narration.volume = this.muted ? 0 : vol;
  }

  setMusicVolume(vol) {
    this.musicVolume = vol;
    if (this.music) this.music.volume = this.muted ? 0 : vol;
  }
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = AudioManager;
}