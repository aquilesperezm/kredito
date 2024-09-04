create table Usuarios(
	id bigserial not null primary key,
	first_name varchar(100) null,
	last_name varchar(100) null,
	type_identification varchar(20) default 'CC' null,
	number_identification varchar(255) null,
	phone varchar(255) null,
	email varchar(255) not null unique,
	password text not null,
	address varchar(255) null,
	address_two varchar(255) null,
	alias varchar(255) null,
	state int default 1 not null,
	created_at timestamp default CURRENT_TIMESTAMP,
	updated_at timestamp default CURRENT_TIMESTAMP
);

create table rolls(
	id bigserial not null primary key,
	name varchar(255) not null,
	code varchar(255) not null unique,
	description varchar(255) not null,
	state int default 1 not null,
	created_at timestamp default CURRENT_TIMESTAMP,
	updated_at timestamp default CURRENT_TIMESTAMP
);

insert into rolls (name, code, description) values ('Administrador', 'JJ0001', 'Administra todo el sistema');
insert into rolls (name, code, description) values ('Manager', 'JJ0002', 'Administra Por Individual sus cuentas');
insert into rolls (name, code, description) values ('Cobrador', 'JJ0003', 'Cobrador');


create table Usuarios_rolls(
	id bigserial not null primary key,
	Usuario_id bigint not null,
	roll_id bigint not null,
	state int default 1 not null,
	created_at timestamp default CURRENT_TIMESTAMP,
	updated_at timestamp default CURRENT_TIMESTAMP,
	CONSTRAINT fk_Usuarios_rolls_Usuario_id
      FOREIGN KEY(Usuario_id) 
	  REFERENCES Usuarios(id),
	CONSTRAINT fk_Usuarios_rolls_roll_id
      FOREIGN KEY(roll_id) 
	  REFERENCES rolls(id)
);

create table clients(
	id bigserial not null primary key,
	first_name varchar(100) null,
	last_name varchar(100) null,
	type_identification varchar(20) default 'CC' null,
	number_identification varchar(255) null,
	phone varchar(255) null,
	email varchar(255) not null unique,
	address varchar(255) null,
	address_two varchar(255) null,
	alias varchar(255) null,
	state int default 1 not null,
	created_at timestamp default CURRENT_TIMESTAMP,
	updated_at timestamp default CURRENT_TIMESTAMP
);

create table Usuarios_clients(
	id bigserial not null primary key,
	Usuario_id bigint not null,
	client_id bigint not null,
	state int default 1 not null,
	created_at timestamp default CURRENT_TIMESTAMP,
	updated_at timestamp default CURRENT_TIMESTAMP,
	CONSTRAINT fk_Usuarios_clients_Usuario_id
      FOREIGN KEY(Usuario_id) 
	  REFERENCES Usuarios(id),
  CONSTRAINT fk_Usuarios_clients_client_id
      FOREIGN KEY(client_id) 
	  REFERENCES clients(id)
);

create table logs(
	id bigserial not null primary key,
	code varchar(255) not null,
	file varchar(255) not null,
	function_failed varchar(255) not null,
	description text,
	state int default 1 not null,
	created_at timestamp default CURRENT_TIMESTAMP,
	updated_at timestamp default CURRENT_TIMESTAMP
);

------------------- desarrollo parte 2 creditos -----

create table interests(
	id bigserial not null primary key,
	value varchar(255) not null,
	state int default 1 not null,
	created_at timestamp default CURRENT_TIMESTAMP,
	updated_at timestamp default CURRENT_TIMESTAMP
);

comment on column interests.value is 'porcentaje del interes';

insert into interests (value)
values ('20');

create table credits(
	id bigserial not null primary key,
	id_client bigint not null,
	owner_Usuario_id bigint not null,
	valor_deuda double(2,2) default 0 null,
	value varchar(255) not null,
	quota integer not null default '60',
	value_paid varchar(255) null default '0',
	utility varchar(255) null default '0',
	id_interest bigint null,
	state int default 1 not null,
	created_at timestamp default CURRENT_TIMESTAMP,
	updated_at timestamp default CURRENT_TIMESTAMP,
	CONSTRAINT fk_credits_id_interest
  	FOREIGN KEY(id_interest) 
	REFERENCES interests(id)
);

comment on column credits.id_client is 'id_client el cual saco el credito';
comment on column credits.owner_Usuario_id is 'due�o o recepcionista del dinero del credito o el que creo el credito';
comment on column credits.value is 'valor total del credito';
comment on column credits.quota is 'cantidad de cuotas que se saca el credito por defecto son 60';
comment on column credits.value_paid is 'valor del credito que se ha pagado a la fecha';
comment on column credits.utility is 'ganancias con los intereses al finalizar el credito';
comment on column credits.id_interest is 'referencia al valor del interes, ya que puede manejar mas de uno, por defecto 20%';

alter table credits add column code varchar(255) null;
alter table credits add column comment text null;

/* 
create table quota(
	id bigserial not null primary key,
	id_credit bigint not null,
	paid_out int default '0' not null,
	value varchar(255) not null,
	state int default 1 not null,
	created_at timestamp default CURRENT_TIMESTAMP,
	updated_at timestamp default CURRENT_TIMESTAMP,
	CONSTRAINT fk_quota_id_credit
  	FOREIGN KEY(id_credit) 
	REFERENCES credits(id)
);

comment on column quota.paid_out is 'se pago la cuota en su totalidad 0 para no, 1 para si';
comment on column quota.value is 'valor de la cuota que debe pagar el cliente'; 
*/
------------------------------------------ Consultas de prueba y desarrollo ----

-------- Parte 3 ------
create table payments(
	id bigserial not null primary key,
	owner_Usuario_id bigint not null,
	id_credit bigint not null,
	way_to_pay varchar(255) not null,
	code_transaction varchar(255) not null,
	description text null,
	value varchar(255) not null,
	state int default 1 not null,
	created_by bigint not null,
	created_at timestamp default CURRENT_TIMESTAMP,
	updated_at timestamp default CURRENT_TIMESTAMP,
	CONSTRAINT fk_payments_id_owner_Usuario_id
  	FOREIGN KEY(owner_Usuario_id) 
	REFERENCES Usuarios(id),
	CONSTRAINT fk_payments_id_credit
  	FOREIGN KEY(id_credit) 
	REFERENCES credits(id),
	CONSTRAINT fk_payments_id_Usuario
  	FOREIGN KEY(created_by) 
	REFERENCES Usuarios(id)
);

comment on column payments.id_credit is 'id_credit a la cual se abona el pago';
comment on column payments.value is 'valor del pago';
comment on column payments.way_to_pay is 'forma de pago';
comment on column payments.code_transaction is 'txid de transaccion';
comment on column payments.value is 'valor del pago';
comment on column payments.owner_Usuario_id is 'due�o o creador de los pagos';

alter table payments add column start_payment_at text null;
alter table payments add column updated_by bigint null;

alter table credits add constraint fk_credits_id_client foreign key(id_client) references clients(id);

alter table Usuarios add column id_owner bigint null;
comment on column Usuarios.id_owner is 'id_Usuario que es due�o de este usuario, relacion a ella misma';
alter table Usuarios add constraint fk_Usuarios_id_owner foreign key(id_owner) references Usuarios(id);

GRANT ALL PRIVILEGES ON TABLE payments TO admin_billrecord;
GRANT ALL PRIVILEGES ON TABLE Usuarios TO admin_billrecord;
GRANT ALL PRIVILEGES ON TABLE credits TO admin_billrecord;
------------------------------------------ Consultas de prueba y desarrollo ----

insert into payments (owner_Usuario_id, id_credit, way_to_pay, code_transaction, description, value)
values('55', '11', 'EFECTIVO', 'a1dV', 'testing', '20000');

select *
from clients c 
order by last_name asc;
select * from logs order by id desc;
select * from interests i2 ;
select * from credits order by id desc;
select * from payments p  order by id desc;
select * from quota;
select * from clients c ;
select * from Usuarios u ;
select * from rolls;

update payments as c 
set start_payment_at ='2022-01-01 14:58:00'
where c.start_payment_at is null;

select p.id as payment_id, p.start_payment_at,c2.number_identification as client_number_identification, c2.first_name as client_first_name, c2.last_name as client_last_name, u.first_name as Usuario_first_name, u.last_name as Usuario_last_name, p.value as payment_value, p.updated_by as payment_updated_by,p.id as payment_id,*, count(p.id) over() as total
                from payments p
                inner join credits c on c.id = p.id_credit 
                inner join clients c2 on c2.id = c.id_client
                left join Usuarios u on u.id = p.updated_by
                where p.owner_Usuario_id ='55'
                and p.state ='1'
                order by p.start_payment_at desc;

select p.value as payment_value,* 
from payments p 
inner join credits c on c.id = p.id_credit 
where p.id ='4';

select p.id as payment_id,*, count(p.id) over() as total
from payments p
inner join credits c on c.id = p.id_credit 
inner join clients c2 on c2.id = c.id_client
where p.owner_Usuario_id ='55'
and p.state ='1'
order by p.updated_at desc
limit 7 offset 0;

insert into credits (id_client, owner_Usuario_id, value, quota, utility, id_interest)
values ('60', '55', '1000000', '60', '1200000', '1');


update credits 
set value = '2000000',
quota = '2',
utility = '2400000',
state = '1',
id_client ='60'
where id ='16';

select *, count(*) over() as total
from clients as c
inner join credits c2 on c2.id_client = c.id
where (email like '%pepito%'
or first_name like '%pepito%'
or last_name like '%pepito%'
or number_identification like '%pepito%')
and c.id in (
        select client_id from Usuarios_clients uc where uc.Usuario_id ='55'
    ) 
and c.state = 1
and c2.state ='1'
and c2.owner_Usuario_id ='55'
limit 7 offset 0;

insert into quota(id_credit, paid_out, value)
values('4', '0', '20000');

select *, count(c.id) over() as total
from clients c
inner join credits c2 on c2.id_client = c.id
where c2.state ='1'
order by c2.value desc
;

select c.id as credit_id,*
from credits c
inner join clients c2 on c2.id = c.id_client 
where c.id ='15';

TRUNCATE TABLE ONLY public.credits RESTART IDENTITY cascade;

select * from logs order by id desc;

select *, count(id) over() as total
from credits c 
where c.owner_Usuario_id ='55'
limit 7 offset 0;


select * from clients;

drop table quota;
drop table credits ;

select * from Usuarios u ;
select * from Usuarios_rolls ur ;
select * from logs order by id desc;
insert into Usuarios(email, password)
values('admin@gmail.com', 'asdf') returning *;

insert into Usuarios_rolls (Usuario_id, roll_id)
values ('45', (select id from rolls r where code ='JJ0002'));

select id from rolls r where code ='JJ0002';
select r.name, r.code, r.description 
from Usuarios_rolls ur
inner join rolls r on r.id = ur.roll_id 
where Usuario_id ='55';

select * from Usuarios u where email = 'admin@gmail.com' and "password" ='gAAAAABicfyUqXmTzw3YCP-BFP72v8Bhp6IKpLf817Ed9HtrEckthIoGN3YIoEvtFDNK5qs0Qgyk-YWC65uqbBxeKu6XlFxfYQ==';

select * from clients c ;
select * from Usuarios_clients uc ;

select *, count(*) OVER() AS full_count
from Usuarios
limit 7 offset 7;

select *, count(*) OVER() AS full_count
from clients as c
where c.id in (
	select client_id from Usuarios_clients uc where uc.Usuario_id ='55'
) and c.state = 1
limit 7 offset 7;

select * from clients c;
select * from Usuarios_clients uc ;

insert into clients(first_name, last_name, type_identification, number_identification, phone, email, address, address_two, alias)
values('', '', 'CC', '', '', 'testy@test.com', '', '', '') returning *;
select * from logs l order by id desc;

select * 
from clients;

insert into Usuarios_clients (Usuario_id, client_id)
values('', '') returning *;

update clients
	set first_name='', 
	last_name='', 
	type_identification='CC', 
	number_identification='', 
	phone='', 
	email='ffff', 
	address='',
	address_two='', 
	alias='',
	state='1',
	updated_at=now() 
where id ='1' returning *;

select *
from clients c 
where id='1';

select * from Usuarios u ;
select * from rolls;

select * from Usuarios_clients uc order by id desc;

select * from logs l order by id desc;

select *
from clients as c
where (email like '%pepito%'
or first_name like '%pepito%'
or last_name like '%pepito%'
or number_identification like '%pepito%')
and c.id in (
        select client_id from Usuarios_clients uc where uc.Usuario_id ='55'
    ) and c.state = 1
limit 7 offset 14;

select * from Usuarios_clients uc ;