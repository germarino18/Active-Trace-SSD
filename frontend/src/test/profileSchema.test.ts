import { describe, it, expect } from 'vitest';
import { personalSchema, bankingSchema } from '@/features/perfil/profileSchema';

describe('personalSchema', () => {
  it('rejects empty nombre', () => {
    const result = personalSchema.safeParse({ nombre: '', apellidos: 'García' });
    expect(result.success).toBe(false);
  });

  it('rejects empty apellidos', () => {
    const result = personalSchema.safeParse({ nombre: 'Juan', apellidos: '' });
    expect(result.success).toBe(false);
  });

  it('accepts valid minimal payload', () => {
    const result = personalSchema.safeParse({ nombre: 'Juan', apellidos: 'García' });
    expect(result.success).toBe(true);
  });

  it('accepts full valid payload', () => {
    const result = personalSchema.safeParse({
      nombre: 'Juan',
      apellidos: 'García',
      dni: '12345678',
      regional: 'Buenos Aires',
      legajo_profesional: 'LP-001',
    });
    expect(result.success).toBe(true);
  });

  it('rejects DNI with less than 7 digits', () => {
    const result = personalSchema.safeParse({ nombre: 'Juan', apellidos: 'García', dni: '123456' });
    expect(result.success).toBe(false);
  });

  it('rejects DNI with more than 8 digits', () => {
    const result = personalSchema.safeParse({ nombre: 'Juan', apellidos: 'García', dni: '123456789' });
    expect(result.success).toBe(false);
  });

  it('accepts DNI with 7 digits', () => {
    const result = personalSchema.safeParse({ nombre: 'Juan', apellidos: 'García', dni: '1234567' });
    expect(result.success).toBe(true);
  });
});

describe('bankingSchema', () => {
  it('rejects CBU with 21 digits', () => {
    const result = bankingSchema.safeParse({ banco: 'Nación', cbu: '123456789012345678901', alias_cbu: '', facturador: false });
    expect(result.success).toBe(false);
    if (!result.success) {
      const cbuError = result.error.issues.find((i) => i.path.includes('cbu'));
      expect(cbuError?.message).toMatch(/22 dígitos/);
    }
  });

  it('accepts CBU with 22 digits', () => {
    const result = bankingSchema.safeParse({ banco: 'Nación', cbu: '1234567890123456789012', alias_cbu: '', facturador: false });
    expect(result.success).toBe(true);
  });

  it('rejects invalid alias (too short)', () => {
    const result = bankingSchema.safeParse({ facturador: false, alias_cbu: 'abc' });
    expect(result.success).toBe(false);
  });

  it('accepts valid alias', () => {
    const result = bankingSchema.safeParse({ facturador: false, alias_cbu: 'juan.garcia' });
    expect(result.success).toBe(true);
  });

  it('accepts empty optional fields', () => {
    const result = bankingSchema.safeParse({ banco: '', cbu: '', alias_cbu: '', facturador: true });
    expect(result.success).toBe(true);
  });

  it('maps facturador true for Factura', () => {
    const result = bankingSchema.safeParse({ facturador: true });
    expect(result.success).toBe(true);
    if (result.success) expect(result.data.facturador).toBe(true);
  });
});
