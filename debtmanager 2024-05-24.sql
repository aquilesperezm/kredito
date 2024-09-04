--
-- PostgreSQL database dump
--

-- Dumped from database version 16.2
-- Dumped by pg_dump version 16.0

-- Started on 2024-05-24 00:46:19

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 221 (class 1259 OID 16906)
-- Name: cliente; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cliente (
    id integer DEFAULT nextval(('public.cliente_id_seq'::text)::regclass) NOT NULL,
    nombres character varying NOT NULL,
    apellidos character varying NOT NULL,
    tipo_de_identificacion_id integer,
    numero_de_identificacion character varying NOT NULL,
    celular character varying NOT NULL,
    telefono character varying NOT NULL,
    email character varying NOT NULL,
    direccion character varying NOT NULL,
    comentarios character varying NOT NULL,
    estado integer NOT NULL,
    referencia_id integer,
    owner_id integer,
    sucursal_id integer,
    created_at date NOT NULL,
    last_edited date NOT NULL
);


ALTER TABLE public.cliente OWNER TO postgres;

--
-- TOC entry 228 (class 1259 OID 17003)
-- Name: cliente_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.cliente_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 2147483647
    CACHE 1;


ALTER SEQUENCE public.cliente_id_seq OWNER TO postgres;

--
-- TOC entry 225 (class 1259 OID 16977)
-- Name: comprobantedepago; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.comprobantedepago (
    id integer DEFAULT nextval(('public.comprobantedepago_id_seq'::text)::regclass) NOT NULL,
    pago_id integer,
    nombre_del_cliente character varying NOT NULL,
    cedula character varying NOT NULL,
    telefono character varying NOT NULL,
    fecha date NOT NULL,
    pendiente integer NOT NULL,
    comentario character varying NOT NULL
);


ALTER TABLE public.comprobantedepago OWNER TO postgres;

--
-- TOC entry 229 (class 1259 OID 17022)
-- Name: comprobantedepago_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.comprobantedepago_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 2147483647
    CACHE 1;


ALTER SEQUENCE public.comprobantedepago_id_seq OWNER TO postgres;

--
-- TOC entry 215 (class 1259 OID 16849)
-- Name: configuracion; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.configuracion (
    id integer DEFAULT nextval(('public.configuracion_id_seq'::text)::regclass) NOT NULL,
    key character varying NOT NULL,
    value character varying NOT NULL
);


ALTER TABLE public.configuracion OWNER TO postgres;

--
-- TOC entry 227 (class 1259 OID 16999)
-- Name: configuracion_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.configuracion_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 2147483647
    CACHE 1;


ALTER SEQUENCE public.configuracion_id_seq OWNER TO postgres;

--
-- TOC entry 222 (class 1259 OID 16928)
-- Name: credito; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.credito (
    id integer DEFAULT nextval(('public.credito_id_seq'::text)::regclass) NOT NULL,
    comentario character varying NOT NULL,
    cobrador_id integer NOT NULL,
    fecha_de_aprobacion date NOT NULL,
    numero_de_cuotas integer NOT NULL,
    tasa_de_interes integer NOT NULL,
    monto integer NOT NULL,
    estado integer NOT NULL,
    frecuencia_del_credito_id integer,
    dias_adicionales integer NOT NULL,
    tipo_de_mora_id integer,
    valor_de_mora integer NOT NULL,
    valor_deuda double precision,
    owner_id integer,
    garante_id integer,
    created_at date NOT NULL,
    last_edited date NOT NULL
);


ALTER TABLE public.credito OWNER TO postgres;

--
-- TOC entry 230 (class 1259 OID 17031)
-- Name: credito_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.credito_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 2147483647
    CACHE 1;


ALTER SEQUENCE public.credito_id_seq OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 16955)
-- Name: cuota; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cuota (
    id integer DEFAULT nextval(('public.cuota_id_seq'::text)::regclass) NOT NULL,
    numero_de_cuota integer NOT NULL,
    fecha_de_pago date NOT NULL,
    fecha_de_aplicacion_de_mora date NOT NULL,
    valor_pagado integer NOT NULL,
    valor_de_cuota integer NOT NULL,
    valor_de_mora integer NOT NULL,
    pagada boolean NOT NULL,
    credito_id integer,
    created_at date NOT NULL,
    last_edited date NOT NULL
);


ALTER TABLE public.cuota OWNER TO postgres;

--
-- TOC entry 231 (class 1259 OID 17045)
-- Name: cuota_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.cuota_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 2147483647
    CACHE 1;


ALTER SEQUENCE public.cuota_id_seq OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 16882)
-- Name: enumerador; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.enumerador (
    id integer DEFAULT nextval(('public.enumerador_id_seq'::text)::regclass) NOT NULL,
    tipo_enumerador_id integer,
    nombre character varying NOT NULL,
    created_at date NOT NULL,
    last_edited date NOT NULL
);


ALTER TABLE public.enumerador OWNER TO postgres;

--
-- TOC entry 232 (class 1259 OID 17049)
-- Name: enumerador_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.enumerador_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 2147483647
    CACHE 1;


ALTER SEQUENCE public.enumerador_id_seq OWNER TO postgres;

--
-- TOC entry 216 (class 1259 OID 16856)
-- Name: exportacion; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.exportacion (
    id integer DEFAULT nextval(('public.exportacion_id_seq'::text)::regclass) NOT NULL,
    sql_reporte character varying NOT NULL,
    codigo character varying NOT NULL,
    nombre character varying NOT NULL,
    activo boolean NOT NULL,
    nombre_archivo character varying NOT NULL,
    comentario character varying NOT NULL
);


ALTER TABLE public.exportacion OWNER TO postgres;

--
-- TOC entry 233 (class 1259 OID 17074)
-- Name: exportacion_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.exportacion_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 2147483647
    CACHE 1;


ALTER SEQUENCE public.exportacion_id_seq OWNER TO postgres;

--
-- TOC entry 224 (class 1259 OID 16965)
-- Name: pago; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pago (
    id integer DEFAULT nextval(('public.pago_id_seq'::text)::regclass) NOT NULL,
    comentario character varying NOT NULL,
    fecha_de_pago date NOT NULL,
    valor_del_pago integer NOT NULL,
    credito_id integer,
    registrado_por_usuario_id integer NOT NULL,
    created_at date NOT NULL,
    last_edited date NOT NULL
);


ALTER TABLE public.pago OWNER TO postgres;

--
-- TOC entry 234 (class 1259 OID 17083)
-- Name: pago_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.pago_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 2147483647
    CACHE 1;


ALTER SEQUENCE public.pago_id_seq OWNER TO postgres;

--
-- TOC entry 226 (class 1259 OID 16989)
-- Name: pagodecuota; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pagodecuota (
    id integer DEFAULT nextval(('public.pagodecuota_id_seq'::text)::regclass) NOT NULL,
    numero_de_cuota integer NOT NULL,
    abonado integer NOT NULL,
    tiene_mora boolean NOT NULL,
    comprobante_id integer
);


ALTER TABLE public.pagodecuota OWNER TO postgres;

--
-- TOC entry 235 (class 1259 OID 17092)
-- Name: pagodecuota_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.pagodecuota_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 2147483647
    CACHE 1;


ALTER SEQUENCE public.pagodecuota_id_seq OWNER TO postgres;

--
-- TOC entry 217 (class 1259 OID 16863)
-- Name: paramexportacion; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.paramexportacion (
    id integer DEFAULT nextval(('public.paramexportacion_id_seq'::text)::regclass) NOT NULL,
    exportacion_id integer,
    nombre character varying NOT NULL,
    codigo character varying NOT NULL,
    tipo_dato character varying NOT NULL,
    comentario character varying NOT NULL,
    obligatorio boolean NOT NULL
);


ALTER TABLE public.paramexportacion OWNER TO postgres;

--
-- TOC entry 236 (class 1259 OID 17096)
-- Name: paramexportacion_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.paramexportacion_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 2147483647
    CACHE 1;


ALTER SEQUENCE public.paramexportacion_id_seq OWNER TO postgres;

--
-- TOC entry 218 (class 1259 OID 16875)
-- Name: tipoenumerador; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tipoenumerador (
    id integer DEFAULT nextval(('public.tipoenumerador_id_seq'::text)::regclass) NOT NULL,
    nombre character varying NOT NULL,
    created_at date NOT NULL,
    last_edited date NOT NULL
);


ALTER TABLE public.tipoenumerador OWNER TO postgres;

--
-- TOC entry 237 (class 1259 OID 17100)
-- Name: tipoenumerador_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tipoenumerador_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 2147483647
    CACHE 1;


ALTER SEQUENCE public.tipoenumerador_id_seq OWNER TO postgres;

--
-- TOC entry 220 (class 1259 OID 16894)
-- Name: usuario; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.usuario (
    id integer DEFAULT nextval(('public.usuario_id_seq'::text)::regclass) NOT NULL,
    login_name character varying NOT NULL,
    password character varying NOT NULL,
    rol_id integer,
    sucursal_id integer,
    nombres character varying,
    apellidos character varying,
    created_at date NOT NULL,
    last_edited date NOT NULL
);


ALTER TABLE public.usuario OWNER TO postgres;

--
-- TOC entry 238 (class 1259 OID 17109)
-- Name: usuario_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.usuario_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 2147483647
    CACHE 1;


ALTER SEQUENCE public.usuario_id_seq OWNER TO postgres;

--
-- TOC entry 4942 (class 0 OID 16906)
-- Dependencies: 221
-- Data for Name: cliente; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.cliente VALUES (586, 'Jonh', 'Smith', 5075, '5222315', '+1 586 984', '+1 586 984', 'jonh.smith@gmail.com', '', '', 1, NULL, NULL, 26, '2024-05-24', '2024-05-24');
INSERT INTO public.cliente VALUES (587, 'James', 'Williams', 5075, '5623487', '+1 234 977', '+1 234 977', 'james.williams@gmail.com', '', '', 1, NULL, NULL, 24, '2024-05-24', '2024-05-24');
INSERT INTO public.cliente VALUES (588, 'Helen', 'Baker', 5075, '5623487', '+1 119 478', '+1 119 478', 'helen.baker@gmail.com', '', '', 1, NULL, NULL, 25, '2024-05-24', '2024-05-24');


--
-- TOC entry 4946 (class 0 OID 16977)
-- Dependencies: 225
-- Data for Name: comprobantedepago; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- TOC entry 4936 (class 0 OID 16849)
-- Dependencies: 215
-- Data for Name: configuracion; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.configuracion VALUES (200, 'cantidad_maxima_de_creditos_por_cliente', '18446744073709551616');


--
-- TOC entry 4943 (class 0 OID 16928)
-- Dependencies: 222
-- Data for Name: credito; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.credito VALUES (196, 'Test Credito', 1, '2024-05-18', 3, 10, 1000, 1, NULL, 2, NULL, 5, 1100, 586, NULL, '2024-05-24', '2024-05-24');


--
-- TOC entry 4944 (class 0 OID 16955)
-- Dependencies: 223
-- Data for Name: cuota; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.cuota VALUES (110, 1, '2024-05-19', '2024-05-20', 23, 12, 2, true, 196, '2024-05-24', '2024-05-24');


--
-- TOC entry 4940 (class 0 OID 16882)
-- Dependencies: 219
-- Data for Name: enumerador; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.enumerador VALUES (5071, 1373, 'Administrador', '2024-05-24', '2024-05-24');
INSERT INTO public.enumerador VALUES (5072, 1373, 'Usuario', '2024-05-24', '2024-05-24');
INSERT INTO public.enumerador VALUES (5073, 1373, 'Cobrador', '2024-05-24', '2024-05-24');
INSERT INTO public.enumerador VALUES (5074, 1374, 'Cédula', '2024-05-24', '2024-05-24');
INSERT INTO public.enumerador VALUES (5075, 1374, 'Cédula Extranjera', '2024-05-24', '2024-05-24');
INSERT INTO public.enumerador VALUES (5076, 1374, 'Pasaporte', '2024-05-24', '2024-05-24');
INSERT INTO public.enumerador VALUES (5077, 1374, 'Nit', '2024-05-24', '2024-05-24');
INSERT INTO public.enumerador VALUES (5078, 1374, 'Tarjeta de identidad', '2024-05-24', '2024-05-24');
INSERT INTO public.enumerador VALUES (5079, 1375, 'Activo', '2024-05-24', '2024-05-24');
INSERT INTO public.enumerador VALUES (5080, 1375, 'Inactivo', '2024-05-24', '2024-05-24');
INSERT INTO public.enumerador VALUES (5081, 1376, 'Diario', '2024-05-24', '2024-05-24');
INSERT INTO public.enumerador VALUES (5082, 1376, 'Semanal', '2024-05-24', '2024-05-24');
INSERT INTO public.enumerador VALUES (5083, 1376, 'Quincenal', '2024-05-24', '2024-05-24');
INSERT INTO public.enumerador VALUES (5084, 1376, 'Mensual', '2024-05-24', '2024-05-24');
INSERT INTO public.enumerador VALUES (5085, 1377, 'Efectivo', '2024-05-24', '2024-05-24');
INSERT INTO public.enumerador VALUES (5086, 1377, 'Transferencia', '2024-05-24', '2024-05-24');
INSERT INTO public.enumerador VALUES (5087, 1377, 'Cheque', '2024-05-24', '2024-05-24');
INSERT INTO public.enumerador VALUES (5088, 1377, 'Item', '2024-05-24', '2024-05-24');
INSERT INTO public.enumerador VALUES (5089, 1377, 'Tarjeta de débito', '2024-05-24', '2024-05-24');
INSERT INTO public.enumerador VALUES (5090, 1377, 'Tarjeta de crédito', '2024-05-24', '2024-05-24');
INSERT INTO public.enumerador VALUES (5091, 1377, 'Otros', '2024-05-24', '2024-05-24');
INSERT INTO public.enumerador VALUES (5092, 1378, 'Valor fijo', '2024-05-24', '2024-05-24');
INSERT INTO public.enumerador VALUES (5093, 1378, 'Porciento', '2024-05-24', '2024-05-24');
INSERT INTO public.enumerador VALUES (5094, 1379, 'Sucursal#1', '2024-05-24', '2024-05-24');
INSERT INTO public.enumerador VALUES (5095, 1379, 'Sucursal#2', '2024-05-24', '2024-05-24');
INSERT INTO public.enumerador VALUES (5096, 1379, 'Sucursal#3', '2024-05-24', '2024-05-24');


--
-- TOC entry 4937 (class 0 OID 16856)
-- Dependencies: 216
-- Data for Name: exportacion; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.exportacion VALUES (397, 'select * from user where id=:mmm', 'dame', 'dame1', true, 'no.txt', 'dsf');
INSERT INTO public.exportacion VALUES (398, 'select * from cliente where created_at BETWEEN :fecha_inicial AND :fecha_final', 'clientes_registrados_en_fecha', 'clientes_registrados_en_fecha', true, 'no.txt', 'Obtiene los clientes registrados entre dos fechas dadas.');


--
-- TOC entry 4945 (class 0 OID 16965)
-- Dependencies: 224
-- Data for Name: pago; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- TOC entry 4947 (class 0 OID 16989)
-- Dependencies: 226
-- Data for Name: pagodecuota; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- TOC entry 4938 (class 0 OID 16863)
-- Dependencies: 217
-- Data for Name: paramexportacion; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.paramexportacion VALUES (586, 397, 'mmm', 'mmm', 'str', '', true);
INSERT INTO public.paramexportacion VALUES (587, 398, 'fecha_inicial', 'fecha_inicial', 'date', 'la fecha minima', true);
INSERT INTO public.paramexportacion VALUES (588, 398, 'fecha_final', 'fecha_final', 'date', 'la fecha maxima', true);


--
-- TOC entry 4939 (class 0 OID 16875)
-- Dependencies: 218
-- Data for Name: tipoenumerador; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.tipoenumerador VALUES (1373, 'Rol de usuario', '2024-05-24', '2024-05-24');
INSERT INTO public.tipoenumerador VALUES (1374, 'Tipo de identificación', '2024-05-24', '2024-05-24');
INSERT INTO public.tipoenumerador VALUES (1375, 'Estado', '2024-05-24', '2024-05-24');
INSERT INTO public.tipoenumerador VALUES (1376, 'Tipo de crédito', '2024-05-24', '2024-05-24');
INSERT INTO public.tipoenumerador VALUES (1377, 'Método de pago', '2024-05-24', '2024-05-24');
INSERT INTO public.tipoenumerador VALUES (1378, 'Tipo de mora', '2024-05-24', '2024-05-24');
INSERT INTO public.tipoenumerador VALUES (1379, 'Tipo de Sucursal', '2024-05-24', '2024-05-24');


--
-- TOC entry 4941 (class 0 OID 16894)
-- Dependencies: 220
-- Data for Name: usuario; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.usuario VALUES (391, 'admin', 'app2002', 5071, 76, 'Peter', 'Jackson', '2024-05-24', '2024-05-24');
INSERT INTO public.usuario VALUES (392, 'usuario1', '55555', 5072, 78, 'Heylen', 'Jones', '2024-05-24', '2024-05-24');


--
-- TOC entry 4965 (class 0 OID 0)
-- Dependencies: 228
-- Name: cliente_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.cliente_id_seq', 588, true);


--
-- TOC entry 4966 (class 0 OID 0)
-- Dependencies: 229
-- Name: comprobantedepago_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.comprobantedepago_id_seq', 1, false);


--
-- TOC entry 4967 (class 0 OID 0)
-- Dependencies: 227
-- Name: configuracion_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.configuracion_id_seq', 200, true);


--
-- TOC entry 4968 (class 0 OID 0)
-- Dependencies: 230
-- Name: credito_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.credito_id_seq', 196, true);


--
-- TOC entry 4969 (class 0 OID 0)
-- Dependencies: 231
-- Name: cuota_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.cuota_id_seq', 110, true);


--
-- TOC entry 4970 (class 0 OID 0)
-- Dependencies: 232
-- Name: enumerador_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.enumerador_id_seq', 5096, true);


--
-- TOC entry 4971 (class 0 OID 0)
-- Dependencies: 233
-- Name: exportacion_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.exportacion_id_seq', 398, true);


--
-- TOC entry 4972 (class 0 OID 0)
-- Dependencies: 234
-- Name: pago_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.pago_id_seq', 1, false);


--
-- TOC entry 4973 (class 0 OID 0)
-- Dependencies: 235
-- Name: pagodecuota_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.pagodecuota_id_seq', 1, false);


--
-- TOC entry 4974 (class 0 OID 0)
-- Dependencies: 236
-- Name: paramexportacion_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.paramexportacion_id_seq', 588, true);


--
-- TOC entry 4975 (class 0 OID 0)
-- Dependencies: 237
-- Name: tipoenumerador_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tipoenumerador_id_seq', 1379, true);


--
-- TOC entry 4976 (class 0 OID 0)
-- Dependencies: 238
-- Name: usuario_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.usuario_id_seq', 392, true);


--
-- TOC entry 4768 (class 2606 OID 17005)
-- Name: cliente cliente_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cliente
    ADD CONSTRAINT cliente_pkey PRIMARY KEY (id);


--
-- TOC entry 4776 (class 2606 OID 17024)
-- Name: comprobantedepago comprobantedepago_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.comprobantedepago
    ADD CONSTRAINT comprobantedepago_pkey PRIMARY KEY (id);


--
-- TOC entry 4756 (class 2606 OID 17001)
-- Name: configuracion configuracion_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.configuracion
    ADD CONSTRAINT configuracion_pkey PRIMARY KEY (id);


--
-- TOC entry 4770 (class 2606 OID 17033)
-- Name: credito credito_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.credito
    ADD CONSTRAINT credito_pkey PRIMARY KEY (id);


--
-- TOC entry 4772 (class 2606 OID 17047)
-- Name: cuota cuota_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cuota
    ADD CONSTRAINT cuota_pkey PRIMARY KEY (id);


--
-- TOC entry 4764 (class 2606 OID 17051)
-- Name: enumerador enumerador_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.enumerador
    ADD CONSTRAINT enumerador_pkey PRIMARY KEY (id);


--
-- TOC entry 4758 (class 2606 OID 17076)
-- Name: exportacion exportacion_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exportacion
    ADD CONSTRAINT exportacion_pkey PRIMARY KEY (id);


--
-- TOC entry 4774 (class 2606 OID 17085)
-- Name: pago pago_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pago
    ADD CONSTRAINT pago_pkey PRIMARY KEY (id);


--
-- TOC entry 4778 (class 2606 OID 17094)
-- Name: pagodecuota pagodecuota_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pagodecuota
    ADD CONSTRAINT pagodecuota_pkey PRIMARY KEY (id);


--
-- TOC entry 4760 (class 2606 OID 17098)
-- Name: paramexportacion paramexportacion_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.paramexportacion
    ADD CONSTRAINT paramexportacion_pkey PRIMARY KEY (id);


--
-- TOC entry 4762 (class 2606 OID 17102)
-- Name: tipoenumerador tipoenumerador_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tipoenumerador
    ADD CONSTRAINT tipoenumerador_pkey PRIMARY KEY (id);


--
-- TOC entry 4766 (class 2606 OID 17111)
-- Name: usuario usuario_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuario
    ADD CONSTRAINT usuario_pkey PRIMARY KEY (id);


--
-- TOC entry 4782 (class 2606 OID 17112)
-- Name: cliente cliente_owner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cliente
    ADD CONSTRAINT cliente_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES public.usuario(id);


--
-- TOC entry 4783 (class 2606 OID 17006)
-- Name: cliente cliente_referencia_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cliente
    ADD CONSTRAINT cliente_referencia_id_fkey FOREIGN KEY (referencia_id) REFERENCES public.cliente(id);


--
-- TOC entry 4784 (class 2606 OID 17057)
-- Name: cliente cliente_tipo_de_identificacion_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cliente
    ADD CONSTRAINT cliente_tipo_de_identificacion_id_fkey FOREIGN KEY (tipo_de_identificacion_id) REFERENCES public.enumerador(id);


--
-- TOC entry 4791 (class 2606 OID 17086)
-- Name: comprobantedepago comprobantedepago_pago_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.comprobantedepago
    ADD CONSTRAINT comprobantedepago_pago_id_fkey FOREIGN KEY (pago_id) REFERENCES public.pago(id);


--
-- TOC entry 4785 (class 2606 OID 17067)
-- Name: credito credito_frecuencia_del_credito_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.credito
    ADD CONSTRAINT credito_frecuencia_del_credito_id_fkey FOREIGN KEY (frecuencia_del_credito_id) REFERENCES public.enumerador(id);


--
-- TOC entry 4786 (class 2606 OID 17011)
-- Name: credito credito_garante_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.credito
    ADD CONSTRAINT credito_garante_id_fkey FOREIGN KEY (garante_id) REFERENCES public.cliente(id);


--
-- TOC entry 4787 (class 2606 OID 17016)
-- Name: credito credito_owner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.credito
    ADD CONSTRAINT credito_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES public.cliente(id);


--
-- TOC entry 4788 (class 2606 OID 17062)
-- Name: credito credito_tipo_de_mora_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.credito
    ADD CONSTRAINT credito_tipo_de_mora_id_fkey FOREIGN KEY (tipo_de_mora_id) REFERENCES public.enumerador(id);


--
-- TOC entry 4789 (class 2606 OID 17034)
-- Name: cuota cuota_credito_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cuota
    ADD CONSTRAINT cuota_credito_id_fkey FOREIGN KEY (credito_id) REFERENCES public.credito(id);


--
-- TOC entry 4780 (class 2606 OID 17103)
-- Name: enumerador enumerador_tipo_enumerador_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.enumerador
    ADD CONSTRAINT enumerador_tipo_enumerador_id_fkey FOREIGN KEY (tipo_enumerador_id) REFERENCES public.tipoenumerador(id);


--
-- TOC entry 4790 (class 2606 OID 17039)
-- Name: pago pago_credito_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pago
    ADD CONSTRAINT pago_credito_id_fkey FOREIGN KEY (credito_id) REFERENCES public.credito(id);


--
-- TOC entry 4792 (class 2606 OID 17025)
-- Name: pagodecuota pagodecuota_comprobante_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pagodecuota
    ADD CONSTRAINT pagodecuota_comprobante_id_fkey FOREIGN KEY (comprobante_id) REFERENCES public.comprobantedepago(id);


--
-- TOC entry 4779 (class 2606 OID 17077)
-- Name: paramexportacion paramexportacion_exportacion_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.paramexportacion
    ADD CONSTRAINT paramexportacion_exportacion_id_fkey FOREIGN KEY (exportacion_id) REFERENCES public.exportacion(id);


--
-- TOC entry 4781 (class 2606 OID 17052)
-- Name: usuario usuario_rol_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuario
    ADD CONSTRAINT usuario_rol_id_fkey FOREIGN KEY (rol_id) REFERENCES public.enumerador(id);


-- Completed on 2024-05-24 00:46:20

--
-- PostgreSQL database dump complete
--

