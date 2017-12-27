CREATE DATABASE IF NOT EXISTS guldandb;

USE guldandb;

CREATE TABLE IF NOT EXISTS `item` (
  `id`                 BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,
  `name`               VARCHAR(255)        NOT NULL,
  `parent_id`          BIGINT(20) UNSIGNED NOT NULL,
  `data`               LONGTEXT,
  `type`               SMALLINT(6)         NOT NULL,
  `current_version_id` BIGINT(20) UNSIGNED          DEFAULT 1,
  `visibility`         SMALLINT(4)         NOT NULL DEFAULT '0',
  `in_grey`            SMALLINT(4)                  DEFAULT 0,
  `is_deleted`         SMALLINT(4)         NOT NULL DEFAULT '0',
  `updated_at`         TIMESTAMP           NOT NULL DEFAULT '1970-01-02 00:00:01' ON UPDATE CURRENT_TIMESTAMP,
  `created_at`         TIMESTAMP           NOT NULL DEFAULT '1970-01-02 00:00:01',
  PRIMARY KEY (`id`),
  KEY `index_isdeleted_parentid` (`is_deleted`, `parent_id`)
)
  ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;

CREATE TABLE IF NOT EXISTS `project` (
  `id`                 BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,
  `name`               VARCHAR(255)        NOT NULL,
  `parent_id`          BIGINT(20) UNSIGNED NOT NULL,
  `visibility`         SMALLINT(4)         NOT NULL DEFAULT '0',
  `current_version_id` BIGINT(20) UNSIGNED          DEFAULT 1,
  `is_deleted`         SMALLINT(4)         NOT NULL DEFAULT '0',
  `updated_at`         TIMESTAMP           NOT NULL DEFAULT '1970-01-02 00:00:01' ON UPDATE CURRENT_TIMESTAMP,
  `created_at`         TIMESTAMP           NOT NULL DEFAULT '1970-01-02 00:00:01',
  PRIMARY KEY (`id`),
  KEY `index_isdeleted_parentid` (`is_deleted`, `parent_id`)
)
  ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;

CREATE TABLE IF NOT EXISTS `org` (
  `id`                 BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,
  `name`               VARCHAR(255)        NOT NULL,
  `visibility`         SMALLINT(4)         NOT NULL DEFAULT '0',
  `current_version_id` BIGINT(20) UNSIGNED          DEFAULT 1,
  `is_deleted`         SMALLINT(4)         NOT NULL DEFAULT '0',
  `updated_at`         TIMESTAMP           NOT NULL DEFAULT '1970-01-02 00:00:01' ON UPDATE CURRENT_TIMESTAMP,
  `created_at`         TIMESTAMP           NOT NULL DEFAULT '1970-01-02 00:00:01',
  PRIMARY KEY (`id`)
)
  ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;

CREATE TABLE IF NOT EXISTS `privilege` (
  `id`                  BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,
  `resource_id`         BIGINT(20) UNSIGNED NOT NULL,
  `resource_name`       VARCHAR(255)        NOT NULL DEFAULT '',
  `resource_type`       SMALLINT(4)         NOT NULL,
  `resource_visibility` SMALLINT(4)         NOT NULL,
  `user_id`             BIGINT(20) UNSIGNED NOT NULL,
  `user_hash`           VARCHAR(32)         NOT NULL DEFAULT '',
  `privilege_type`      SMALLINT(4)         NOT NULL,
  `is_deleted`          SMALLINT(4)         NOT NULL DEFAULT '0',
  `updated_at`          TIMESTAMP           NOT NULL DEFAULT '1970-01-02 00:00:01' ON UPDATE CURRENT_TIMESTAMP,
  `created_at`          TIMESTAMP           NOT NULL DEFAULT '1970-01-02 00:00:01',
  PRIMARY KEY (`id`),
  KEY `index_isdeleted_resourcetype_privilegetype` (`is_deleted`, `resource_type`, `privilege_type`)
)
  ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;

CREATE TABLE IF NOT EXISTS `user` (
  `id`          BIGINT(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  `name`        VARCHAR(64)         NOT NULL DEFAULT '',
  `user_hash`   VARCHAR(32)         NOT NULL DEFAULT '',
  `secret_hash` VARCHAR(32)         NOT NULL DEFAULT '',
  `is_deleted`  SMALLINT(4)         NOT NULL DEFAULT '0',
  `updated_at`  TIMESTAMP           NOT NULL DEFAULT '1970-01-02 00:00:01' ON UPDATE CURRENT_TIMESTAMP,
  `created_at`  TIMESTAMP           NOT NULL DEFAULT '1970-01-02 00:00:01',
  PRIMARY KEY (`id`)
)
  ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;

CREATE TABLE IF NOT EXISTS `user_login` (
  `id`          BIGINT(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id`     BIGINT(20) UNSIGNED NOT NULL,
  `login_token` VARCHAR(64)         NOT NULL DEFAULT '',
  `is_deleted`  SMALLINT(4)         NOT NULL DEFAULT '0',
  `updated_at`  TIMESTAMP           NOT NULL DEFAULT '1970-01-02 00:00:01' ON UPDATE CURRENT_TIMESTAMP,
  `created_at`  TIMESTAMP           NOT NULL DEFAULT '1970-01-02 00:00:01',
  PRIMARY KEY (`id`)
)
  ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;

CREATE TABLE IF NOT EXISTS `audit` (
  `id`            BIGINT(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id`       BIGINT(20) UNSIGNED NOT NULL,
  `action`        SMALLINT(4)         NOT NULL,
  `resource_id`   BIGINT(20)          NOT NULL DEFAULT 0,
  `resource_type` SMALLINT(4)         NOT NULL,
  `version_id`    BIGINT(20) UNSIGNED          DEFAULT 1,
  `is_deleted`    SMALLINT(4)         NOT NULL DEFAULT '0',
  `updated_at`    TIMESTAMP           NOT NULL DEFAULT '1970-01-02 00:00:01' ON UPDATE CURRENT_TIMESTAMP,
  `created_at`    TIMESTAMP           NOT NULL DEFAULT '1970-01-02 00:00:01',
  PRIMARY KEY (`id`),
  KEY `index_isdeleted_resourceid` (`is_deleted`, `resource_id`)
)
  ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;

CREATE TABLE IF NOT EXISTS `version` (
  `id`                  BIGINT(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  `resource_id`         BIGINT(20) UNSIGNED NOT NULL,
  `resource_type`       SMALLINT(4)         NOT NULL,
  `version_id`          BIGINT(20) UNSIGNED NOT NULL,
  `resource_content`    LONGTEXT            NOT NULL,
  `resource_visibility` SMALLINT(4)         NOT NULL,
  `type`                SMALLINT(4)                  DEFAULT 0,
  `is_deleted`          SMALLINT(4)         NOT NULL DEFAULT 0,
  `updated_at`          TIMESTAMP           NOT NULL DEFAULT '1970-01-02 00:00:01' ON UPDATE CURRENT_TIMESTAMP,
  `created_at`          TIMESTAMP           NOT NULL DEFAULT '1970-01-02 00:00:01',
  PRIMARY KEY (`id`),
  KEY `index_isdeleted_resourceid_resourcetype` (`is_deleted`, `resource_id`, `resource_type`)
)
  ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;

CREATE TABLE IF NOT EXISTS `grey_item` (
  `id`                 BIGINT(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  `item_id`            BIGINT(20) UNSIGNED NOT NULL,
  `item_name`          VARCHAR(255)        NOT NULL,
  `item_data`          LONGTEXT            NOT NULL,
  `item_type`          SMALLINT(4)         NOT NULL,
  `item_visibility`    SMALLINT(4)         NOT NULL,
  `is_deleted`         SMALLINT(4)         NOT NULL DEFAULT 0,
  `current_version_id` BIGINT(20) UNSIGNED          DEFAULT 1,
  `updated_at`         TIMESTAMP           NOT NULL DEFAULT '1970-01-02 00:00:01' ON UPDATE CURRENT_TIMESTAMP,
  `created_at`         TIMESTAMP           NOT NULL DEFAULT '1970-01-02 00:00:01',
  PRIMARY KEY (`id`),
  KEY `index_isdeleted_itemid` (`is_deleted`, `item_id`)
)
  ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;

CREATE TABLE IF NOT EXISTS `sequence_dual` (
  `id`            BIGINT(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  `sequence_name` VARCHAR(128) UNIQUE NOT NULL,
  `value`         BIGINT(20) UNSIGNED NOT NULL DEFAULT 1,
  `is_deleted`    SMALLINT(4)         NOT NULL DEFAULT 0,
  `updated_at`    TIMESTAMP           NOT NULL DEFAULT '1970-01-02 00:00:01' ON UPDATE CURRENT_TIMESTAMP,
  `created_at`    TIMESTAMP           NOT NULL DEFAULT '1970-01-02 00:00:01',
  PRIMARY KEY (`id`)
)
  ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4;
