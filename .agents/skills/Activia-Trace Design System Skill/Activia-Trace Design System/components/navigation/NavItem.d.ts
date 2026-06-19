import React from "react";

export interface NavItemProps {
  /** Material Symbols glyph name */
  icon: string;
  label: string;
  active?: boolean;
  href?: string;
  onClick?: (e: React.MouseEvent) => void;
  /** Count chip on the right */
  badge?: number | string;
  style?: React.CSSProperties;
}

/** Sidebar navigation row with violet active state + right accent bar. */
export function NavItem(props: NavItemProps): JSX.Element;
