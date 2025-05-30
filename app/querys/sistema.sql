-- phpMyAdmin SQL Dump
-- version 5.2.1deb1
-- https://www.phpmyadmin.net/
--
-- Servidor: localhost:3306
-- Tiempo de generación: 14-05-2025 a las 20:14:30
-- Versión del servidor: 10.11.11-MariaDB-0+deb12u1
-- Versión de PHP: 8.2.28

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

--
-- Base de datos: `EndoRayo`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `mod_images`
--

CREATE TABLE `mod_images` (
  `mod_img_id` int(11) NOT NULL,
  `mod_img_name` varchar(100) DEFAULT NULL,
  `mod_img_path` varchar(100) DEFAULT NULL,
  `mod_img_date` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `mod_images`
--

INSERT INTO `mod_images` (`mod_img_id`, `mod_img_name`, `mod_img_path`, `mod_img_date`) VALUES
(15, '1.jpg', 'media/uploads/1.jpg', '2025-04-26 00:33:30'),
(22, 'Captura_de_pantalla_2025-04-23_11-09-23.png', 'media/uploads/Captura_de_pantalla_2025-04-23_11-09-23.png', '2025-05-06 21:17:44'),
(26, 'Captura de pantalla_2025-05-06_18-55-32.png', 'media/uploads/Captura de pantalla_2025-05-06_18-55-32.png', '2025-05-06 21:45:18'),
(28, '7.jpg', 'media/uploads/7.jpg', '2025-05-06 22:19:10'),
(29, '22.jpg', 'media/uploads/22.jpg', '2025-05-06 22:19:39'),
(30, '57.jpg', 'media/uploads/57.jpg', '2025-05-06 22:20:05');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `mod_paciente`
--

CREATE TABLE `mod_paciente` (
  `mod_pac_id` int(11) NOT NULL,
  `mod_pac_ci` varchar(20) NOT NULL,
  `mod_pac_nombre` varchar(100) NOT NULL,
  `mod_pac_apellido` varchar(100) NOT NULL,
  `mod_pac_fecha_nacimiento` date DEFAULT NULL,
  `mod_pac_telefono` varchar(20) DEFAULT NULL,
  `mod_pac_direccion` varchar(255) DEFAULT NULL,
  `mod_pac_email` varchar(100) DEFAULT NULL,
  `mod_pac_form_diag` int(11) DEFAULT NULL,
  `mod_pac_observaciones` text DEFAULT NULL,
  `mod_pac_fecha_registro` timestamp NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `mod_paciente`
--

INSERT INTO `mod_paciente` (`mod_pac_id`, `mod_pac_ci`, `mod_pac_nombre`, `mod_pac_apellido`, `mod_pac_fecha_nacimiento`, `mod_pac_telefono`, `mod_pac_direccion`, `mod_pac_email`, `mod_pac_form_diag`, `mod_pac_observaciones`, `mod_pac_fecha_registro`) VALUES
(11, '9249563', 'Jhonatan', 'Arias', '2025-04-03', '123123123', 'Calle 2', 'rojasmijael67@gmail.com', 9, 'Cosas', '2025-04-26 04:19:06'),
(12, '123123', 'Mijael', 'Rojas', '2025-04-11', '123123', 'Calle 2', 'rojasmijael67@gmail.com', 10, 'Cositas', '2025-04-26 04:20:46'),
(13, '777', 'michelle', 'Rocha', '2025-04-25', '123', 'Calle 2', 'rojasmijael67@gmail.com', 11, 'Cositas', '2025-04-26 04:48:35'),
(14, '123', '123', '123', '2025-05-24', '123', '123', '213@gmail.com', 12, '213', '2025-05-07 02:17:44');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `mod_paciente_revision`
--

CREATE TABLE `mod_paciente_revision` (
  `mod_pac_rev_id` int(11) NOT NULL,
  `mod_pac_rev_dolor_persistente` tinyint(1) DEFAULT NULL,
  `mod_pac_rev_sensibilidad_prolongada` tinyint(1) DEFAULT NULL,
  `mod_pac_rev_hinchazon` tinyint(1) DEFAULT NULL,
  `mod_pac_rev_fistula` tinyint(1) DEFAULT NULL,
  `mod_pac_rev_cambio_color` tinyint(1) DEFAULT NULL,
  `mod_pac_rev_dolor_percusion` tinyint(1) DEFAULT NULL,
  `mod_pac_rev_movilidad` tinyint(1) DEFAULT NULL,
  `mod_pac_rev_caries_profunda` tinyint(1) DEFAULT NULL,
  `mod_pac_rev_lesion_radiografica` tinyint(1) DEFAULT NULL,
  `mod_pac_rev_observaciones` text DEFAULT NULL,
  `mod_pac_rev_fecha` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `mod_paciente_revision`
--

INSERT INTO `mod_paciente_revision` (`mod_pac_rev_id`, `mod_pac_rev_dolor_persistente`, `mod_pac_rev_sensibilidad_prolongada`, `mod_pac_rev_hinchazon`, `mod_pac_rev_fistula`, `mod_pac_rev_cambio_color`, `mod_pac_rev_dolor_percusion`, `mod_pac_rev_movilidad`, `mod_pac_rev_caries_profunda`, `mod_pac_rev_lesion_radiografica`, `mod_pac_rev_observaciones`, `mod_pac_rev_fecha`) VALUES
(4, 0, 0, 1, 0, 1, 0, 0, 0, 0, 'q', '2025-04-25 23:07:58'),
(8, 1, 0, 1, 0, 0, 1, 0, 0, 0, 'Cositaas', '2025-04-26 00:19:15'),
(9, 0, 0, 1, 1, 0, 1, 0, 0, 0, 'Cositas', '2025-04-26 00:19:55'),
(10, 0, 1, 0, 0, 0, 1, 0, 0, 0, 'Cositas', '2025-04-26 00:20:54'),
(11, 0, 1, 0, 1, 0, 0, 0, 0, 0, 'Sin cositas', '2025-04-26 00:48:45'),
(12, 0, 0, 1, 1, 0, 1, 0, 0, 0, '', '2025-05-06 22:17:56');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `mod_user`
--

CREATE TABLE `mod_user` (
  `user_id` int(11) NOT NULL,
  `name` varchar(50) NOT NULL,
  `lastname` varchar(50) NOT NULL,
  `username` varchar(100) NOT NULL,
  `email` varchar(150) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `created_at` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `mod_user_paciente`
--

CREATE TABLE `mod_user_paciente` (
  `user_paciente` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `paciente` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `paciente_imagen`
--

CREATE TABLE `paciente_imagen` (
  `id` int(11) NOT NULL,
  `paciente_id` int(11) NOT NULL,
  `imagen_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `paciente_imagen`
--

INSERT INTO `paciente_imagen` (`id`, `paciente_id`, `imagen_id`) VALUES
(4, 11, 15),
(11, 11, 22),
(15, 12, 26),
(17, 11, 28),
(18, 12, 29),
(19, 13, 30);

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `mod_images`
--
ALTER TABLE `mod_images`
  ADD PRIMARY KEY (`mod_img_id`);

--
-- Indices de la tabla `mod_paciente`
--
ALTER TABLE `mod_paciente`
  ADD PRIMARY KEY (`mod_pac_id`),
  ADD UNIQUE KEY `mod_pac_ci` (`mod_pac_ci`);

--
-- Indices de la tabla `mod_paciente_revision`
--
ALTER TABLE `mod_paciente_revision`
  ADD PRIMARY KEY (`mod_pac_rev_id`);

--
-- Indices de la tabla `mod_user`
--
ALTER TABLE `mod_user`
  ADD PRIMARY KEY (`user_id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Indices de la tabla `mod_user_paciente`
--
ALTER TABLE `mod_user_paciente`
  ADD PRIMARY KEY (`user_paciente`);

--
-- Indices de la tabla `paciente_imagen`
--
ALTER TABLE `paciente_imagen`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `mod_images`
--
ALTER TABLE `mod_images`
  MODIFY `mod_img_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=31;

--
-- AUTO_INCREMENT de la tabla `mod_paciente`
--
ALTER TABLE `mod_paciente`
  MODIFY `mod_pac_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=15;

--
-- AUTO_INCREMENT de la tabla `mod_paciente_revision`
--
ALTER TABLE `mod_paciente_revision`
  MODIFY `mod_pac_rev_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT de la tabla `mod_user`
--
ALTER TABLE `mod_user`
  MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `mod_user_paciente`
--
ALTER TABLE `mod_user_paciente`
  MODIFY `user_paciente` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `paciente_imagen`
--
ALTER TABLE `paciente_imagen`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=20;
COMMIT;
