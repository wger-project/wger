-- CREATE TABLE "manager_exercisecategory" (
--     "id" integer NOT NULL PRIMARY KEY,
--     "name" varchar(100) NOT NULL
-- );
INSERT INTO "manager_exercisecategory" VALUES(1,'Arme');
INSERT INTO "manager_exercisecategory" VALUES(2,'Beine');
INSERT INTO "manager_exercisecategory" VALUES(3,'Bauch');

-- CREATE TABLE "manager_exercise" (
--     "id" integer NOT NULL PRIMARY KEY,
--     "category_id" integer NOT NULL REFERENCES "manager_exercisecategory" ("id"),
--     "name" varchar(200) NOT NULL
-- );
INSERT INTO "manager_exercise" VALUES(1,1,'Trizeps Seildrücken');
INSERT INTO "manager_exercise" VALUES(2,2,'Bizeps am Kabel');
INSERT INTO "manager_exercise" VALUES(3,2,'Beinpresse');
INSERT INTO "manager_exercise" VALUES(4,2,'Kniebeuge');
INSERT INTO "manager_exercise" VALUES(5,3,'Crunches');
INSERT INTO "manager_exercise" VALUES(6,1,'Curls');
INSERT INTO "manager_exercise" VALUES(7,2,'Ausfallschritte');