import { gsap } from 'gsap';
gsap.from('.card', { y: 40, opacity: 0, ease: 'bounce.out', stagger: 0.1 });
gsap.to('.panel', { width: 400, duration: 1 });
