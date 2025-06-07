-- Añadir campo paciente_id a la tabla mod_paciente_revision para relacionar revisiones con pacientes
ALTER TABLE mod_paciente_revision ADD COLUMN mod_pac_rev_paciente_id INT NOT NULL;

-- Actualizar las revisiones existentes con su paciente correspondiente
UPDATE mod_paciente_revision r
JOIN mod_paciente p ON p.mod_pac_form_diag = r.mod_pac_rev_id
SET r.mod_pac_rev_paciente_id = p.mod_pac_id;

-- Crear índice para optimizar búsquedas
CREATE INDEX idx_mod_pac_rev_paciente_id ON mod_paciente_revision(mod_pac_rev_paciente_id);

-- Agregar relación de clave foránea (solo en caso de usar InnoDB)
ALTER TABLE mod_paciente_revision 
ADD CONSTRAINT fk_paciente_revision 
FOREIGN KEY (mod_pac_rev_paciente_id) 
REFERENCES mod_paciente(mod_pac_id) 
ON DELETE CASCADE;
