import React from "react";

export interface TagProps {
  children?: React.ReactNode;
  /** Material Symbols glyph name */
  icon?: string;
  /** Show a close affordance and call this on click */
  onRemove?: (e: React.MouseEvent) => void;
  style?: React.CSSProperties;
}

/** Low-emphasis metadata chip (subject codes, filters, categories). */
export function Tag(props: TagProps): JSX.Element;
