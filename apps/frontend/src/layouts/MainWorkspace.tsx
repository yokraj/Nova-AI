import React from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { cn } from '@/utils/cn';

export const MainWorkspace: React.FC = () => {
  const location = useLocation();
  const isDashboard = location.pathname === '/' || location.pathname === '';

  return (
    <main className="flex-1 min-w-0 h-full overflow-y-auto bg-[#02040a] relative">
      <motion.div
        key={location.pathname}
        initial={{ opacity: 0, y: 6 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.2, ease: 'easeOut' }}
        className={cn(
          'w-full h-full min-w-0',
          !isDashboard && 'p-4 sm:p-6 max-w-7xl mx-auto'
        )}
      >
        <Outlet />
      </motion.div>
    </main>
  );
};

export default MainWorkspace;
