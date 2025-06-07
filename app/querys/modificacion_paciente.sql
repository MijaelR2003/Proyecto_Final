-- Modificación de la tabla de pacientes para separar apellidos y agregar campos adicionales

-- 1. Primero creamos una copia temporal de los datos actuales
CREATE TABLE `mod_paciente_temp` LIKE `mod_paciente`;
INSERT INTO `mod_paciente_temp` SELECT * FROM `mod_paciente`;

-- 2. Modificamos la tabla principal
ALTER TABLE `mod_paciente` 
ADD COLUMN `mod_pac_apellido_paterno` VARCHAR(50) NOT NULL AFTER `mod_pac_nombre`,
ADD COLUMN `mod_pac_apellido_materno` VARCHAR(50) NULL AFTER `mod_pac_apellido_paterno`,
ADD COLUMN `mod_pac_genero` ENUM('Masculino', 'Femenino', 'Otro') NULL AFTER `mod_pac_fecha_nacimiento`,
ADD COLUMN `mod_pac_ocupacion` VARCHAR(100) NULL AFTER `mod_pac_genero`,
ADD COLUMN `mod_pac_alergias` TEXT NULL AFTER `mod_pac_ocupacion`;

-- 3. Migramos los datos del apellido actual a apellido paterno
UPDATE `mod_paciente` SET `mod_pac_apellido_paterno` = `mod_pac_apellido`;

-- 4. Creamos un índice para búsquedas más rápidas
ALTER TABLE `mod_paciente` 
ADD INDEX `idx_paciente_apellidos` (`mod_pac_apellido_paterno`, `mod_pac_apellido_materno`),
ADD INDEX `idx_paciente_nombres` (`mod_pac_nombre`);

-- 5. Nota: Esta sentencia solo se ejecutará al final cuando todo funcione correctamente
-- ALTER TABLE `mod_paciente` DROP COLUMN `mod_pac_apellido`;
