export class TweenRunner {
  constructor() {
    this.activeTweens = new Set();
  }

  tween({ duration = 650, ease = TweenRunner.easeInOutCubic, onUpdate, onComplete }) {
    const startedAt = performance.now();
    const tween = { cancelled: false };
    this.activeTweens.add(tween);

    const step = (now) => {
      if (tween.cancelled) {
        this.activeTweens.delete(tween);
        return;
      }

      const progress = Math.min((now - startedAt) / duration, 1);
      const eased = ease(progress);
      onUpdate(eased);

      if (progress < 1) {
        requestAnimationFrame(step);
        return;
      }

      this.activeTweens.delete(tween);
      onComplete?.();
    };

    requestAnimationFrame(step);
    return () => {
      tween.cancelled = true;
    };
  }

  static easeInOutCubic(t) {
    return t < 0.5 ? 4 * t * t * t : 1 - ((-2 * t + 2) ** 3) / 2;
  }
}