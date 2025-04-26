'use client';

import * as React from 'react';
import { motion } from 'framer-motion';

export interface TextareaProps
  extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {}

const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, ...props }, ref) => {
    const [isFocused, setIsFocused] = React.useState(false);

    return (
      <div className="relative">
        <motion.textarea
          ref={ref}
          className="flex min-h-[80px] w-full rounded-md border border-gray-200 bg-white px-3 py-2 text-sm ring-offset-white placeholder:text-gray-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-400 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          {...props}
        />
        <motion.div
          className="absolute inset-0 rounded-md pointer-events-none"
          initial={false}
          animate={{
            boxShadow: isFocused
              ? '0 0 0 2px rgba(59, 130, 246, 0.5)'
              : '0 0 0 0px rgba(59, 130, 246, 0)'
          }}
          transition={{ duration: 0.2 }}
        />
      </div>
    );
  }
);

Textarea.displayName = 'Textarea';

export { Textarea }; 