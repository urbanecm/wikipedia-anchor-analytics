DROP TABLE IF EXISTS links;
CREATE TABLE links
(
	link_id int primary key auto_increment not null,
	link_source_page_id int not null,
	link_source_page_title varchar(255) not null,
	link_target_page_title varchar(255) not null,
	link_anchor varchar(255)
);

DROP TABLE IF EXISTS anchors;
CREATE TABLE anchors
(
	anchor_id int primary key auto_increment not null,
	anchor_page_id int not null,
	anchor_page_title varchar(255) not null,
	anchor_name varchar(255) not null
);
