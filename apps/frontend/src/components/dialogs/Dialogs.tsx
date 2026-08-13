import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, AlertTriangle } from 'lucide-react';
import { PrimaryButton, DangerButton, SecondaryButton } from '../ui/Buttons';
import { cn } from '@/utils/cn';

export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  className?: string;
}

export const Modal: React.FC<ModalProps> = ({ isOpen, onClose, title, children, className }) => (
  <AnimatePresence>
    {isOpen && (
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
          className="absolute inset-0 bg-slate-950/80 backdrop-blur-sm"
        />
        <motion.div
          initial={{ scale: 0.95, opacity: 0, y: 10 }}
          animate={{ scale: 1, opacity: 1, y: 0 }}
          exit={{ scale: 0.95, opacity: 0, y: 10 }}
          className={cn('glass-panel-cyan p-6 rounded-2xl border border-cyan-500/30 max-w-lg w-full z-10 space-y-4 shadow-2xl relative', className)}
        >
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <h3 className="text-lg font-extrabold text-cyan-300 cyber-glow-text">{title}</h3>
            <button onClick={onClose} className="p-1 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-slate-200">
              <X className="w-4 h-4" />
            </button>
          </div>
          <div>{children}</div>
        </motion.div>
      </div>
    )}
  </AnimatePresence>
);

export const Drawer: React.FC<ModalProps> = ({ isOpen, onClose, title, children, className }) => (
  <AnimatePresence>
    {isOpen && (
      <div className="fixed inset-0 z-50 flex justify-end">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
          className="absolute inset-0 bg-slate-950/80 backdrop-blur-sm"
        />
        <motion.div
          initial={{ x: 400 }}
          animate={{ x: 0 }}
          exit={{ x: 400 }}
          transition={{ duration: 0.25, ease: 'easeInOut' }}
          className={cn('glass-panel h-full w-96 border-l border-slate-800 p-6 z-10 space-y-4 overflow-y-auto relative', className)}
        >
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <h3 className="text-base font-bold text-slate-100">{title}</h3>
            <button onClick={onClose} className="p-1 rounded-lg hover:bg-slate-800 text-slate-400">
              <X className="w-4 h-4" />
            </button>
          </div>
          <div>{children}</div>
        </motion.div>
      </div>
    )}
  </AnimatePresence>
);

export const ConfirmationDialog: React.FC<{
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string;
}> = ({ isOpen, onClose, onConfirm, title, message }) => (
  <Modal isOpen={isOpen} onClose={onClose} title={title}>
    <div className="space-y-4">
      <div className="flex items-start space-x-3 text-amber-400">
        <AlertTriangle className="w-6 h-6 flex-shrink-0 mt-0.5" />
        <p className="text-xs text-slate-300">{message}</p>
      </div>
      <div className="flex justify-end space-x-3 pt-2">
        <SecondaryButton onClick={onClose}>Cancel</SecondaryButton>
        <DangerButton onClick={() => { onConfirm(); onClose(); }}>Confirm Action</DangerButton>
      </div>
    </div>
  </Modal>
);
