CREATE TABLE animals (
	name VARCHAR(255) PRIMARY KEY NOT NULL,
	size VARCHAR(255) NOT NULL,
	description VARCHAR(255) NOT NULL,
	imagedir VARCHAR(255) NOT NULL
);

INSERT INTO animals (name, size, description, imagedir) VALUES
('kangaroo', 'large', 'the humble kangaroo. tends to hop around a lot', './static/img/kangaroo'),
('emu', 'medium', 'the emu needs no introduction. so i''m not going to give it one', './static/img/emu'),
('quokka', 'small', 'the quokka is scientifically the cutest animal to live', './static/img/quokka');