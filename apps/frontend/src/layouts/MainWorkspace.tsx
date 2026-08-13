import React from 'react';
import { Outlet } from 'react-router-dom';
import { motion } from 'framer-motion';

export const MainWorkspace: React.FC = () => {
  return (
    <main className="flex-1 h-[calc(100vh-4rem)] overflow-y-auto p-6 bg-slate-950/60 relative">
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.25, ease: 'easeOut' }}
        className="max-w-7xl mx-auto space-y-6"
      >
        <Outlet />
      </motion.div>
    </main>
  );
};

export default MainWorkspace;
