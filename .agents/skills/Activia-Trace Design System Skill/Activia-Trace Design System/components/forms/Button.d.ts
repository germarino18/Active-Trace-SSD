import React from "react";

export type ButtonVariant = "primary" | "secondary" | "tertiary" | "ghost" | "danger";
export type ButtonSize = "sm" | "md" | "lg";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  /** Visual style. @default "primary" */
  variant?: ButtonVariant;
  /** @default "md" */
  size?: ButtonSize;
  /** Material Symbols glyph name shown before the label */
  icon?: string;
  /** Material Symbols glyph name shown after the label */
  trailingIcon?: string;
  /** Stretch to container width */
  fullWidth?: boolean;
  children?: React.ReactNode;
}

/**
 * Primary action control.
 * @startingPoint section="Forms" subtitle="Buttons in every variant + size" viewport="700x180"
 */
export function Button(props: ButtonProps): JSX.Element;
