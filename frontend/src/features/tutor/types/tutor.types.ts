export interface TutorAlumno {
  id: string;
  nombre: string;
  apellido: string;
  email: string;
  materia_nombre: string;
  comision: string;
}

export interface Guardia {
  id: string;
  fecha: string;
  materia_nombre: string;
  hora_inicio: string;
  hora_fin: string;
  estado: string;
  comision?: string;
  observaciones?: string;
}

export interface GuardiasResponse {
  items: Guardia[];
  total: number;
}

export interface RegistrarGuardiaData {
  tipo: 'guardia';
  fecha: string;
  hora_inicio: string;
  hora_fin: string;
  materia_id: string;
  comision?: string;
  observaciones?: string;
}
