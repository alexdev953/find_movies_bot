PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "Untitled" (
  "id" INTEGER NOT NULL,
  "userid" INTEGER NOT NULL,
  "username" TEXT,
  "firstname" TEXT,
  "lastname" TEXT,
  "create_date" DATETIME DEFAULT DATETIME,
  "update_date" DATETIME,
  PRIMARY KEY ("id"),
  CONSTRAINT "unique_id" UNIQUE ("id")
);
CREATE TABLE IF NOT EXISTS "users" (
  "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  "userid" INTEGER NOT NULL,
  "username" TEXT DEFAULT Null,
  "firstname" TEXT DEFAULT Null,
  "lastname" TEXT DEFAULT Null,
  "create_date" DATETIME DEFAULT (datetime('now', 'localtime')),
  "last_uses" DATETIME,
  CONSTRAINT "unique_id" UNIQUE ("id" ASC)
);
INSERT INTO users VALUES(6,379210271,'taras_303','Taras','None','2021-05-08 07:39:46','2021-05-13 22:35:08');
CREATE TABLE IF NOT EXISTS "films" (
  "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  "films_id" INTEGER NOT NULL,
  "name" TEXT NOT NULL,
  "url" TEXT NOT NULL,
  "poster_url" TEXT NOT NULL,
  "created" DATETIME DEFAULT (datetime('now', 'localtime')),
  CONSTRAINT "check_unique_films" UNIQUE ("films_id" ASC) ON CONFLICT IGNORE,
  CONSTRAINT "check_unique_id" UNIQUE ("id" ASC)
);
INSERT INTO films VALUES(201,27583,'Земля кочевников','http://baskino.me/films/dramy/27583-zemlya-kochevnikov.html','http://baskino.me/uploads/images/2021/255/oidm193.jpg','2021-05-08 11:52:58');
DELETE FROM sqlite_sequence;
INSERT INTO sqlite_sequence VALUES('users',10);
INSERT INTO sqlite_sequence VALUES('films',676);
COMMIT;
