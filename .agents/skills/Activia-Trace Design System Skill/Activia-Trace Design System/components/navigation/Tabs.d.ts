import React from "react";

export interface TabItem {
  id: string;
  label: string;
  /** Material Symbols glyph name */
  icon?: string;
  /** Count chip */
  badge?: number | string;
}

export interface TabsProps {
  tabs: TabItem[];
  /** Active tab id */
  value: string;
  onChange?: (id: string) => void;
  style?: React.CSSProperties;
}

/**
 * Underlined horizontal tab bar (Materias sub-views).
 * @startingPoint section="Navigation" subtitle="Tabs & sidebar nav items" viewport="700x120"
 */
export function Tabs(props: TabsProps): JSX.Element;
