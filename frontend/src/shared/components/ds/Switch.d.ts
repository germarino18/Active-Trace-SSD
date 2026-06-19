import React from "react";

export interface SwitchProps {
  checked?: boolean;
  onChange?: (next: boolean) => void;
  disabled?: boolean;
  /** Optional text label to the right */
  label?: string;
  id?: string;
}

/** Material-style toggle switch (violet track when on). */
export function Switch(props: SwitchProps): JSX.Element;
