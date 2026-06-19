import React from "react";

export interface TextareaProps extends Omit<React.TextareaHTMLAttributes<HTMLTextAreaElement>, "style"> {
  label?: string;
  helper?: string;
  error?: string;
  style?: React.CSSProperties;
}

/** Multi-line text field matching Input's visual language. */
export function Textarea(props: TextareaProps): JSX.Element;
