import React from 'react';
import { cn } from '@/utils/cn';
import { TableBlockData } from '../types/message';

interface TableBlockProps {
  data: TableBlockData;
  className?: string;
}

export const TableBlock: React.FC<TableBlockProps> = ({ data, className }) => {
  return (
    <div className={cn('my-3 rounded-2xl bg-slate-950 border border-slate-800/90 overflow-hidden shadow-xl', className)}>
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs font-mono">
          <thead className="bg-slate-900/90 text-cyan-300 border-b border-slate-800 uppercase tracking-wider font-bold">
            <tr>
              {data.headers.map((h, idx) => (
                <th key={idx} className="px-4 py-3 border-r border-slate-800/60 last:border-0 whitespace-nowrap">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 text-slate-200">
            {data.rows.map((row, rIdx) => (
              <tr key={rIdx} className="hover:bg-slate-900/40 transition-colors">
                {row.map((cell, cIdx) => (
                  <td key={cIdx} className="px-4 py-3 border-r border-slate-800/40 last:border-0 whitespace-nowrap">
                    {cell}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default TableBlock;
