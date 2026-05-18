"use client";

import { useCallback, useEffect, useRef, useState } from "react";

/**
 * Debounced autosave helper. Returns a `mark()` to call from input handlers
 * and a `savedAt` epoch ms timestamp the `AutoSaveIndicator` consumes.
 */
export function usePersistOnBlur<T>(
  value: T,
  persist: (v: T) => Promise<void>,
  options: { debounceMs?: number } = {},
) {
  const { debounceMs = 500 } = options;
  const [savedAt, setSavedAt] = useState<number | null>(null);
  const valueRef = useRef(value);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  valueRef.current = value;

  const flush = useCallback(async () => {
    await persist(valueRef.current);
    setSavedAt(Date.now());
  }, [persist]);

  const mark = useCallback(() => {
    if (timerRef.current) clearTimeout(timerRef.current);
    timerRef.current = setTimeout(() => {
      void flush();
    }, debounceMs);
  }, [debounceMs, flush]);

  useEffect(() => {
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, []);

  return { mark, flush, savedAt };
}
