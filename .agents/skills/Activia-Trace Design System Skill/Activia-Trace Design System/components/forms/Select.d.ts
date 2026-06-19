import React from "react";

export interface SelectOption { value: string; label: string; }

export interface SelectProps extends Omit<React.SelectHTMLAttributes<HTMLSelectElement>, "style"> {
  label?: string;
  /** Provide options OR <option> children */
  options?: SelectOption[];
  placeholder?: string;
  error?: string;
  style?: React.CSSProperties;
}

/** Native select styled to match Input, with chevron affordance. */
export function Select(props: SelectProps): JSX.Element;
