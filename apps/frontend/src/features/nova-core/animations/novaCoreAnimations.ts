import { Variants } from 'framer-motion';
import { NovaCoreState } from '../types/novaCore';

export const coreHaloVariants: Record<NovaCoreState, any> = {
  IDLE: {
    scale: [1, 1.03, 1],
    opacity: [0.5, 0.75, 0.5],
    transition: { duration: 4, repeat: Infinity, ease: 'easeInOut' },
  },
  LISTENING: {
    scale: [1, 1.08, 1],
    opacity: [0.8, 1, 0.8],
    transition: { duration: 1.2, repeat: Infinity, ease: 'easeInOut' },
  },
  THINKING: {
    rotate: 360,
    opacity: [0.7, 0.95, 0.7],
    transition: { rotate: { duration: 8, repeat: Infinity, ease: 'linear' }, opacity: { duration: 2, repeat: Infinity } },
  },
  PLANNING: {
    rotate: -360,
    scale: [1, 1.05, 1],
    transition: { rotate: { duration: 6, repeat: Infinity, ease: 'linear' }, scale: { duration: 2, repeat: Infinity } },
  },
  EXECUTING: {
    scale: [1, 1.07, 1],
    opacity: [0.85, 1, 0.85],
    transition: { duration: 1.8, repeat: Infinity, ease: 'easeInOut' },
  },
  SPEAKING: {
    scale: [1, 1.04, 1],
    opacity: [0.75, 0.95, 0.75],
    transition: { duration: 0.9, repeat: Infinity, ease: 'easeInOut' },
  },
  SUCCESS: {
    scale: [1, 1.06, 1],
    opacity: 1,
    transition: { duration: 0.5 },
  },
  ERROR: {
    scale: [1, 1.05, 1],
    opacity: 1,
    transition: { duration: 0.5 },
  },
};
