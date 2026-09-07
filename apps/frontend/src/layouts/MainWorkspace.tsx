import React from 'react';
import { Outlet } from 'react-router-dom';
import { motion } from 'framer-motion';

export const MainWorkspace: React.FC = () => {
  return (
    <main className="flex-1 min-w-0 h-[calc(100vh-4.25rem)] overflow-y-auto p-3 sm:p-6 bg-slate-950/60 relative">
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.2, ease: 'easeOut' }}
        className="max-w-6xl mx-auto space-y-6 min-w-0 w-full"
      >
        <Outlet />
      </motion.div>
    </main>
  );
};

export default MainWorkspace;
