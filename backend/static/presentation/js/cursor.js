// Cursor animation system
class CursorAnimator {
  constructor(element) {
    this.element = element;
    this.x = 0;
    this.y = 0;
    this.targetX = 0;
    this.targetY = 0;
    this.isMoving = false;
    this.isClicking = false;
  }

  moveTo(x, y, duration = 1000) {
    return new Promise((resolve) => {
      const startX = this.x;
      const startY = this.y;
      const startTime = performance.now();

      const animate = (currentTime) => {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        // Ease in-out
        const eased = progress < 0.5
          ? 2 * progress * progress
          : 1 - Math.pow(-2 * progress + 2, 2) / 2;

        this.x = startX + (x - startX) * eased;
        this.y = startY + (y - startY) * eased;
        this.updatePosition();

        if (progress < 1) {
          requestAnimationFrame(animate);
        } else {
          resolve();
        }
      };

      requestAnimationFrame(animate);
    });
  }

  updatePosition() {
    if (this.element) {
      this.element.style.left = this.x + 'px';
      this.element.style.top = this.y + 'px';
    }
  }

  click() {
    this.isClicking = true;
    if (this.element) {
      this.element.classList.add('clicking');
      setTimeout(() => {
        this.element.classList.remove('clicking');
        this.isClicking = false;
      }, 200);
    }
  }

  hide() {
    if (this.element) {
      this.element.style.opacity = '0';
    }
  }

  show() {
    if (this.element) {
      this.element.style.opacity = '1';
    }
  }

  // Simulate typing at a position
  async type(duration = 2000) {
    const steps = 20;
    const stepDuration = duration / steps;
    for (let i = 0; i < steps; i++) {
      this.click();
      await new Promise(r => setTimeout(r, stepDuration));
    }
  }

  // Smooth scroll to a position
  async scrollTo(targetY, duration = 1000) {
    const startY = window.scrollY;
    const startTime = performance.now();
    
    return new Promise((resolve) => {
      const animate = (currentTime) => {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const eased = progress < 0.5
          ? 2 * progress * progress
          : 1 - Math.pow(-2 * progress + 2, 2) / 2;
        
        window.scrollTo(0, startY + (targetY - startY) * eased);
        
        if (progress < 1) {
          requestAnimationFrame(animate);
        } else {
          resolve();
        }
      };
      requestAnimationFrame(animate);
    });
  }
}

// Export for use in player
if (typeof module !== 'undefined' && module.exports) {
  module.exports = CursorAnimator;
}