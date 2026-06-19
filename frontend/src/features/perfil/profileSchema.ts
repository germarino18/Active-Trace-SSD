import { z } from 'zod';

export const personalSchema = z.object({
  nombre: z.string().min(1, 'El nombre es requerido'),
  apellidos: z.string().min(1, 'El apellido es requerido'),
  dni: z
    .string()
    .regex(/^\d{7,8}$/, 'El DNI debe tener 7 u 8 dígitos')
    .optional()
    .or(z.literal('')),
  regional: z.string().max(100, 'Máximo 100 caracteres').optional().or(z.literal('')),
  legajo_profesional: z.string().max(50, 'Máximo 50 caracteres').optional().or(z.literal('')),
});

export const bankingSchema = z.object({
  banco: z.string().max(100, 'Máximo 100 caracteres').optional().or(z.literal('')),
  cbu: z
    .string()
    .regex(/^\d{22}$/, 'El CBU debe tener 22 dígitos')
    .optional()
    .or(z.literal('')),
  alias_cbu: z
    .string()
    .regex(/^[a-zA-Z0-9.\-]{6,20}$/, 'El alias debe tener entre 6 y 20 caracteres alfanuméricos')
    .optional()
    .or(z.literal('')),
  facturador: z.boolean(),
});

export type PersonalForm = z.infer<typeof personalSchema>;
export type BankingForm = z.infer<typeof bankingSchema>;
