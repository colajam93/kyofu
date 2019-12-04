CREATE DATABASE IF NOT EXISTS kyofu;

USE `kyofu`;

CREATE TABLE IF NOT EXISTS library (
  library_id INT(20) NOT NULL AUTO_INCREMENT,
  name varchar(100) NOT NULL,
  base_path varchar(500) NOT NULL,
  PRIMARY KEY(library_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS song (
  song_id INT(20) NOT NULL AUTO_INCREMENT,
  library_id INT(20) NOT NULL,
  title VARCHAR(200) NOT NULL,
  album VARCHAR(200) NOT NULL,
  artist VARCHAR(200) NOT NULL,
  album_artist VARCHAR(200) DEFAULT NULL,
  genre VARCHAR(50) NOT NULL,
  track_number SMALLINT(2) NOT NULL,
  disc_number SMALLINT(2) NOT NULL,
  release_year SMALLINT(4) NOT NULL,
  modified DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  file_path VARCHAR(500) NOT NULL,
  PRIMARY KEY(song_id),
  INDEX `i_song_1` (title),
  INDEX `i_song_2` (album),
  INDEX `i_song_3` (artist),
  INDEX `i_song_4` (album_artist),
  INDEX `i_song_5` (genre),
  UNIQUE KEY `u_song_1` (file_path),
  FOREIGN KEY `f_song_1` (library_id) REFERENCES library(library_id) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;
