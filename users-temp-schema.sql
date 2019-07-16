SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';
SET @OLD_TIME_ZONE=@@session.time_zone;

DROP SCHEMA IF EXISTS `ghtorrent-users-temp` ;
CREATE SCHEMA IF NOT EXISTS `ghtorrent-users-temp` DEFAULT CHARACTER SET utf8 ;
USE `ghtorrent-users-temp` ;

-- -----------------------------------------------------
-- Table `ghtorrent`.`users`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `ghtorrent-users-temp`.`users` ;

CREATE TABLE IF NOT EXISTS `ghtorrent-users-temp`.`users` (
  `login` VARCHAR(255) NOT NULL COMMENT '',
  `name` VARCHAR(255) NULL DEFAULT NULL COMMENT '',
  `email` VARCHAR(255) NULL DEFAULT NULL COMMENT '')
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;