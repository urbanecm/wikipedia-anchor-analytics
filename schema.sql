DROP TABLE IF EXISTS page;
CREATE TABLE page
(
	page_id int primary key not null,
	page_title varchar(255) not null,
	page_link_processed boolean default true not null,
	page_anchor_processed boolean default true not null
);

DROP TABLE IF EXISTS link;
CREATE TABLE link
(
	link_id int primary key auto_increment not null,
	link_source_page_id int not null,
	link_source_page_title varchar(255) not null,
	link_target_page_title varchar(255) not null,
	link_anchor varchar(255)
);

DROP TABLE IF EXISTS anchor;
CREATE TABLE anchor
(
	anchor_id int primary key auto_increment not null,
	anchor_page_id int not null,
	anchor_page_title varchar(255) not null,
	anchor_name varchar(255) not null
);
