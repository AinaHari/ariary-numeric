// Subtitle system
class SubtitleManager {
  constructor(container) {
    this.container = container;
    this.currentSubtitle = null;
    this.isVisible = false;
  }

  show(text, duration = 3000) {
    if (this.currentSubtitle) {
      this.currentSubtitle.classList.remove('visible');
    }

    const subtitle = document.createElement('div');
    subtitle.className = 'subtitle';
    subtitle.innerHTML = text;
    this.container.appendChild(subtitle);

    // Trigger reflow
    subtitle.offsetHeight;
    subtitle.classList.add('visible');

    this.currentSubtitle = subtitle;

    if (duration > 0) {
      setTimeout(() => {
        subtitle.classList.remove('visible');
        setTimeout(() => {
          if (subtitle.parentNode) {
            subtitle.parentNode.removeChild(subtitle);
          }
          if (this.currentSubtitle === subtitle) {
            this.currentSubtitle = null;
          }
        }, 300);
      }, duration);
    }
  }

  hide() {
    if (this.currentSubtitle) {
      this.currentSubtitle.classList.remove('visible');
      setTimeout(() => {
        if (this.currentSubtitle && this.currentSubtitle.parentNode) {
          this.currentSubtitle.parentNode.removeChild(this.currentSubtitle);
        }
        this.currentSubtitle = null;
      }, 300);
    }
  }

  clear() {
    if (this.container) {
      this.container.innerHTML = '';
    }
    this.currentSubtitle = null;
  }
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = SubtitleManager;
}