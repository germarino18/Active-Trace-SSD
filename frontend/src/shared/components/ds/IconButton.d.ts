import React from "react";

export interface IconButtonProps {
  /** Material Symbols glyph name */
  icon: string;
  size?: "sm" | "md" | "lg";
  variant?: "ghost" | "solid" | "outline";
  /** Violet active state */
  active?: boolean;
  /** Red notification dot (top-right) */
  dot?: boolean;
  disabled?: boolean;
  /** Accessible label / tooltip */
  label?: string;
  onClick?: (e: React.MouseEvent<HTMLButtonElement>) => void;
  style?: React.CSSProperties;
}

/** Icon-only square control for headers, toolbars, and table rows. */
export function IconButton(props: IconButtonProps): JSX.Element;
