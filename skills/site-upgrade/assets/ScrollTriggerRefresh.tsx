'use client';

import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { useEffect } from 'react';

if (typeof window !== 'undefined') {
  gsap.registerPlugin(ScrollTrigger);
}

/**
 * ScrollTrigger measures each trigger's position once. When the page changes height afterwards
 * (web fonts swapping in, late images, accordions, tabs, filtered lists), triggers near the end of
 * the page can sit beyond the maximum scroll and never fire, leaving their content invisible.
 *
 * Mount this once in the layout. It re-measures when fonts and images have loaded, and again,
 * debounced, whenever the body's size changes. It renders nothing.
 */
const ScrollTriggerRefresh = () => {
  useEffect(() => {
    const refresh = () => ScrollTrigger.refresh();

    document.fonts?.ready.then(refresh).catch(() => {});
    window.addEventListener('load', refresh);

    let pending: ReturnType<typeof setTimeout> | undefined;
    const observer = new ResizeObserver(() => {
      clearTimeout(pending);
      pending = setTimeout(refresh, 150);
    });
    observer.observe(document.body);

    return () => {
      window.removeEventListener('load', refresh);
      observer.disconnect();
      clearTimeout(pending);
    };
  }, []);

  return null;
};

export default ScrollTriggerRefresh;
