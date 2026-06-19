import React from "react";

export interface ProgressSegment { value: number; color?: string; }

export interface ProgressBarProps {
  /** 0–100 */
  value?: number;
  tone?: "primary" | "success";
  height?: number;
  /** Uppercase caption above the bar */
  label?: string;
  /** Show the percentage on the right */
  showValue?: boolean;
  /** Multi-color stacked segments (graded/pending/incomplete) */
  segments?: ProgressSegment[];
  style?: React.CSSProperties;
}

/** Thin progress track; supports single value or stacked segments. */
export function ProgressBar(props: ProgressBarProps): JSX.Element;
