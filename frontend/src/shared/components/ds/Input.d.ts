import React from "react";

export interface InputProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, "style"> {
  /** Uppercase label above the field */
  label?: string;
  /** Material Symbols glyph shown inside, on the left */
  icon?: string;
  /** Helper text below the field */
  helper?: string;
  /** Error message — turns border + text red */
  error?: string;
  /** Fully rounded (search bars) */
  pill?: boolean;
  style?: React.CSSProperties;
}

/** Text field with label, leading icon, helper/error, and violet focus ring. */
export function Input(props: InputProps): JSX.Element;
