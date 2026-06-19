import React from "react";

export interface CheckboxProps {
  checked?: boolean;
  onChange?: (next: boolean) => void;
  disabled?: boolean;
  label?: string;
  id?: string;
}

/** Square checkbox with violet fill + check glyph when selected. */
export function Checkbox(props: CheckboxProps): JSX.Element;
