import React from "react";

export interface StatCardProps {
  label: string;
  value: React.ReactNode;
  /** Small unit suffix (e.g. "%") */
  unit?: string;
  /** Trend caption (e.g. "+4% from last term") */
  trend?: string;
  trendDir?: "up" | "down";
  /** Material Symbols glyph name */
  icon?: string;
  /** 0–100 progress bar at the bottom */
  progress?: number;
  /** "primary" = filled violet highlight tile */
  tone?: "default" | "primary";
  style?: React.CSSProperties;
}

/** KPI tile: big number, label, optional trend + progress bar. */
export function StatCard(props: StatCardProps): JSX.Element;
